#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["servicex-local==1.2.1", "func-adl-servicex-xaodr25", "uproot", "awkward"]
# ///
"""Scan fired Run 3 HLT chains for retained features and offline jet matches.

This uses the local Windows/WSL2 ServiceX adaptor. See the trigger reference for
the aarch64 runner workaround and for how to interpret mixed validity links.
"""

import argparse
import ast
import csv
import json
import logging
import math
import re
import shutil
from collections import defaultdict
from pathlib import Path
from typing import Tuple, TypeVar

import awkward as ak
import uproot
from func_adl import ObjectStream, func_adl_callable
from func_adl_servicex_xaodr25 import FuncADLQueryPHYS, FuncADLQueryPHYSLITE
from servicex import Sample, ServiceXSpec, dataset
from servicex_local.adaptor import SXLocalAdaptor
from servicex_local.codegen import LocalXAODCodegen
from servicex_local.deliver import deliver
from servicex_local.science_images import WSL2ScienceImage

T = TypeVar("T")
CHAIN_PATTERN = "HLT_j.*"
JET_KEY = "AnalysisJets"
MATCH_DR = 0.2
HLT_SUMMARY = "HLTNav_Summary_DAODSlimmed"


def _add_tools(s: ObjectStream[T]) -> ObjectStream[T]:
    return s.MetaData({
        "metadata_type": "inject_code", "name": "scan_run3_tools",
        "header_includes": [
            "AsgTools/AnaToolHandle.h", "TrigConfInterfaces/ITrigConfigTool.h",
            "TrigDecisionTool/TrigDecisionTool.h", "TrigCompositeUtils/TrigCompositeUtils.h",
            "TriggerMatchingTool/IMatchingTool.h", "TriggerMatchingTool/IMatchScoringTool.h",
            "TriggerMatchingTool/R3MatchingTool.h", "xAODJet/JetContainer.h",
        ],
        "private_members": [
            "asg::AnaToolHandle<TrigConf::ITrigConfigTool> m_scanConf;",
            "asg::AnaToolHandle<Trig::TrigDecisionTool> m_scanTDT;",
            "asg::AnaToolHandle<Trig::IMatchScoringTool> m_scanScore;",
            "asg::AnaToolHandle<Trig::IMatchingTool> m_scanMatch;",
        ],
        "instance_initialization": [
            'm_scanConf("TrigConf::xAODConfigTool/xAODConfigTool")',
            'm_scanTDT("Trig::TrigDecisionTool/TrigDecisionTool")',
            'm_scanScore("Trig::DRScoringTool/DRScoringTool")',
            'm_scanMatch("Trig::R3MatchingTool/R3MatchingTool")',
        ],
        "initialize_lines": [
            "ANA_CHECK(m_scanConf.initialize());",
            'ANA_CHECK(m_scanTDT.setProperty("ConfigTool", m_scanConf.getHandle()));',
            'ANA_CHECK(m_scanTDT.setProperty("TrigDecisionKey", "xTrigDecision"));',
            'ANA_CHECK(m_scanTDT.setProperty("NavigationFormat", "TrigComposite"));',
            f'ANA_CHECK(m_scanTDT.setProperty("HLTSummary", {json.dumps(HLT_SUMMARY)}));',
            "ANA_CHECK(m_scanTDT.initialize());",
            "ANA_CHECK(m_scanScore.initialize());",
            'ANA_CHECK(m_scanMatch.setProperty("TrigDecisionTool", m_scanTDT.getHandle()));',
            'ANA_CHECK(m_scanMatch.setProperty("ScoringTool", m_scanScore.getHandle()));',
            "ANA_CHECK(m_scanMatch.initialize());",
        ],
        "link_libraries": [
            "TriggerMatchingToolLib", "TrigDecisionToolLib", "TrigConfInterfaces", "xAODJet",
        ],
    })


def _scan_processor(s: ObjectStream[T], a: ast.Call) -> Tuple[ObjectStream[T], ast.Call]:
    pattern = json.dumps(CHAIN_PATTERN)
    jet_key = json.dumps(JET_KEY)
    dr = repr(MATCH_DR)
    new_s = s.MetaData({
        "metadata_type": "add_cpp_function", "name": "scan_run3_matching",
        "include_files": ["vector", "string", "xAODJet/JetContainer.h"],
        "arguments": [],
        "code": [
            "std::vector<std::string> result;",
            "const xAOD::JetContainer* offline_jets = nullptr;",
            f"ANA_CHECK(evtStore()->retrieve(offline_jets, {jet_key}));",
            f"for (const auto& name : m_scanTDT->getChainGroup({pattern})->getListOfTriggers()) {{",
            "  if (!m_scanTDT->isPassed(name)) continue;",
            "  Trig::FeatureRequestDescriptor frd(name);",
            "  auto features = m_scanTDT->features<xAOD::IParticleContainer>(frd);",
            "  int n_valid = 0;",
            "  for (const auto& feature : features) if (feature.isValid()) ++n_valid;",
            "  int n_matched = -2; // No valid particle feature: matching not attempted.",
            "  if (n_valid > 0 && static_cast<size_t>(n_valid) != features.size()) {",
            "    n_matched = -1; // Mixed links: R3MatchingTool may throw Bad link info.",
            "  } else if (n_valid > 0) {",
            "    n_matched = 0;",
            f"    for (const auto* jet : *offline_jets) if (m_scanMatch->match(*jet, name, {dr}, false)) ++n_matched;",
            "  }",
            '  result.push_back(name + "|" + std::to_string(features.size()) + "|" + std::to_string(n_valid) + "|" + std::to_string(n_matched));',
            "}",
        ],
        "result_name": "result", "return_type": "std::vector<std::string>",
    })
    return _add_tools(new_s), a


@func_adl_callable(_scan_processor)
def scan_run3_matching() -> list[str]:
    ...


def summarize(root_path: Path, output_dir: Path) -> None:
    stats = defaultdict(lambda: [0] * 8)
    with uproot.open(root_path) as root_file:
        tree = root_file["atlas_xaod_tree"]
        records = tree.arrays(["scan"], library="ak")["scan"]
        for record in ak.to_list(ak.flatten(records)):
            chain, n_total, n_valid, n_matched = record.rsplit("|", 3)
            total, valid, matched = int(n_total), int(n_valid), int(n_matched)
            row = stats[chain]
            row[0] += 1  # fired events
            row[1] += total > 0
            row[2] += valid > 0
            row[3] += total > 0 and valid == total
            row[4] += matched == -1
            row[5] += matched > 0
            row[6] += max(matched, 0)
            row[7] = max(row[7], valid)
        csv_path = output_dir / "trigger_matching_counts.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow([
                "chain", "fired_events", "feature_events", "valid_feature_events",
                "clean_link_events", "mixed_link_events", "matched_events",
                "matched_jets", "max_valid_links",
            ])
            for chain, row in sorted(stats.items()):
                writer.writerow([chain, *row])
        print(json.dumps({
            "events_examined": tree.num_entries,
            "fired_chains": len(stats),
            "chains_with_features": sum(row[1] > 0 for row in stats.values()),
            "chains_with_valid_links": sum(row[2] > 0 for row in stats.values()),
            "chains_with_offline_jet_matches": sum(row[5] > 0 for row in stats.values()),
            "csv": str(csv_path),
        }, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", type=Path, help="Local Run 3 PHYSLITE ROOT file")
    source.add_argument("--read-root", type=Path, help="Summarize an already produced ServiceX output ROOT file")
    parser.add_argument("--out", type=Path, required=True, help="Output directory outside the repository")
    parser.add_argument("--release", default="25.2.80", help="Installed AnalysisBase 25.2 release")
    parser.add_argument("--data-format", choices=("physlite", "phys"), default="physlite")
    parser.add_argument("--hlt-summary", default="HLTNav_Summary_DAODSlimmed", help="Run 3 summary container found in the file")
    parser.add_argument("--pattern", default="HLT_j.*", help="Narrow TDT chain regex")
    parser.add_argument("--jet-key", default="AnalysisJets", help="Offline jet StoreGate key")
    parser.add_argument("--dr", type=float, default=0.2, help="Run 3 matching threshold")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    if args.read_root:
        if not args.read_root.is_file():
            parser.error(f"Output ROOT file does not exist: {args.read_root}")
        saved_root = args.out / "trigger_matching_scan.root"
        if args.read_root.resolve() != saved_root.resolve():
            shutil.copy2(args.read_root, saved_root)
        summarize(saved_root, args.out)
        return
    if not args.input.is_file():
        parser.error(f"Input file does not exist: {args.input}")
    if not re.fullmatch(r"[A-Za-z0-9_.*?+-]+", args.pattern):
        parser.error("--pattern must be a simple trigger-name regex")
    if not re.fullmatch(r"[A-Za-z0-9_]+", args.jet_key):
        parser.error("--jet-key must be a StoreGate key without punctuation")
    if not re.fullmatch(r"[A-Za-z0-9_]+", args.hlt_summary):
        parser.error("--hlt-summary must be a StoreGate key without punctuation")
    if not math.isfinite(args.dr) or args.dr <= 0:
        parser.error("--dr must be positive and finite")
    global CHAIN_PATTERN, JET_KEY, MATCH_DR, HLT_SUMMARY
    CHAIN_PATTERN, JET_KEY, MATCH_DR, HLT_SUMMARY = (
        args.pattern, args.jet_key, args.dr, args.hlt_summary,
    )
    logging.basicConfig(level=logging.INFO, force=True)
    base_query = FuncADLQueryPHYSLITE() if args.data_format == "physlite" else FuncADLQueryPHYS()
    query = base_query.Select(lambda event: {"scan": scan_run3_matching()})
    spec = ServiceXSpec(Sample=[Sample(
        Name="trigger_matching_scan", Dataset=dataset.FileList([str(args.input)]), Query=query,
    )])
    adaptor = SXLocalAdaptor(
        LocalXAODCodegen(), WSL2ScienceImage("atlas_al9", args.release),
        args.out / "cache", "http://localhost:5001",
    )
    roots = deliver(spec, adaptor=adaptor, ignore_local_cache=True, display_progress=False)["trigger_matching_scan"]
    if len(roots) != 1:
        raise RuntimeError(f"Expected one output file, got {roots}")
    saved_root = args.out / "trigger_matching_scan.root"
    shutil.copy2(roots[0], saved_root)
    summarize(saved_root, args.out)


if __name__ == "__main__":
    main()
