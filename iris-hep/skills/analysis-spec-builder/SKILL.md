---
name: analysis-spec-builder
description: >-
  Use when producing a structured ATLAS analysis specification document:
  formalizing an analysis design into a specification.md file, documenting
  signal/control/validation regions, background methods, systematic
  uncertainties, and statistical model choices, or when the
  atlas-analysis-planner agent needs to write its output to disk.
---

# Analysis Specification Builder

## Overview

This is a workflow skill — not a library. It guides the production of a
structured `specification.md` document that serves as the blueprint for an ATLAS
physics analysis. A good specification is detailed enough for a graduate student
to execute and a physics group convener to sign off on.

## When to Use

- After `atlas-analysis-planner` has designed an analysis and needs to write
  output
- When a user asks to document an analysis design they have already thought
  through
- When creating the input for `atlas-data-plotter` (which reads
  `specification.md` before writing code)
- For internal notes, preliminary results, or paper-level analysis blueprints

## Template

Write `specification.md` with the following sections. Fill every section — a
missing section is a flag for the convener.

```markdown
# Analysis Specification: <Physics Title>

**Status:** Draft | Preliminary | Final **Date:** YYYY-MM-DD **Authors:**
<names>

---

## 1. Physics Motivation

<1–3 paragraphs: what is the signal, why is it interesting, what are the
existing experimental results (cite ATLAS/CMS papers), what is the expected
sensitivity, what luminosity and collision energy are targeted>

---

## 2. Datasets

### Data

| Campaign          | Luminosity | GRL                  |
| ----------------- | ---------- | -------------------- |
| Run 2 (2015–2018) | 139 fb⁻¹   | GRL*data18_13TeV*... |

### MC Samples

| Process          | Generator      | DSID range    | Campaign  | Notes     |
| ---------------- | -------------- | ------------- | --------- | --------- |
| Signal (WW→lνlν) | Sherpa 2.2.11  | 364250–364255 | mc20e     | ...       |
| ttbar            | Powheg+Pythia8 | 410470        | mc20a/c/e | inclusive |

All containers verified in AMI with `--data-type DAOD_PHYSLITE`.

---

## 3. Framework and Software

| Component     | Choice              | Notes                        |
| ------------- | ------------------- | ---------------------------- |
| Ntupling      | TopCPToolkit vX.Y   | standard object selection    |
| Analysis      | Python / coffea     | reads NTuples produced above |
| Statistics    | pyhf + cabinetry    | HistFactory JSON workspace   |
| ATLAS release | AthAnalysis, 25.2.X | or AnalysisBase              |

---

## 4. Object Selection

### Jets

- Collection: `AnalysisJets` (PHYSLITE) / `AntiKt4EMPFlowJets` (PHYS)
- pT > 25 GeV, |η| < 2.5
- JVT > 0.5 for pT < 60 GeV, |η| < 2.4
- CP tool: `JetCalibTool` + `JetUncertaintiesTool`

### Electrons

- WP: `TightLH` + gradient isolation
- pT > 27 GeV, |η_cluster| < 2.47, excluding 1.37–1.52
- CP tool: `EgammaCalibrationAndSmearingTool`

### Muons

- WP: `Medium` + FCLoose isolation
- pT > 27 GeV, |η| < 2.5
- CP tool: `MuonCalibrationAndSmearingTool`

### b-jets

- WP: DL1dv01 at 77% efficiency
- CP tool: `BTaggingEfficiencyTool`

### Overlap Removal

Order: electrons → muons → jets (AntiKt4 ΔR < 0.2 e-jet, ΔR < 0.4 jet-e/μ)

---

## 5. Region Definitions

### Signal Region (SR)

| Cut     | Value     | Motivation                |
| ------- | --------- | ------------------------- |
| Njets   | ≥ 4       | require hadronic activity |
| Nb-jets | ≥ 2       | suppress W+jets           |
| MET     | > 200 GeV | reduce QCD                |
| ...     |           |                           |

Expected yields (pre-fit): S = XX ± YY, B = ZZ ± WW (stat. only)

### Control Region: ttbar (CR_top)

<Definition, expected purity, statistics>

### Control Region: W+jets (CR_Wjets)

<Definition>

### Validation Region (VR_top)

<Definition — orthogonal to CR, between CR and SR in MET>

---

## 6. Background Estimation

| Background | Method                         | Region             | Purity |
| ---------- | ------------------------------ | ------------------ | ------ |
| ttbar      | MC normalized in CR_top        | CR_top             | ~85%   |
| W+jets     | MC normalized in CR_Wjets      | CR_Wjets           | ~70%   |
| Multi-jet  | Data-driven matrix method      | dedicated loose SR | —      |
| Diboson    | MC (normalization free in fit) | —                  | —      |

---

## 7. Systematic Uncertainties

### Experimental (NPs constrained to Gaussian)

- JES (23 components, 3 leading): ±1–5%
- JER (8 components): ±1–3%
- b-tagging efficiency (eigenvectors): ±1–5% per jet
- Lepton efficiency, energy scale/resolution: ±0.5–2%
- MET soft-term: ±5%
- Pile-up reweighting: ±5%
- Luminosity: ±1.5% (Run 2)

### Modelling

- ttbar generator: Powheg+H7 vs Powheg+P8 comparison
- ttbar shower: Powheg+P8 vs Sherpa 2.2.11
- Signal QCD scale: envelope of μ_R, μ_F variations
- Signal PDF: PDF4LHC15 eigenvectors

---

## 8. Statistical Model

- Framework: pyhf (HistFactory JSON) via cabinetry
- Fit type: profile likelihood, background-only for exclusion
- POI: signal strength μ
- Regions in fit: SR + CR_top + CR_Wjets simultaneously
- NP treatment: correlated across regions where applicable
- MC stat. uncertainty: Barlow-Beeston lite
- Test statistic: CLs (for exclusion limits)

---

## 9. Unblinding Checklist

- [ ] MC modelling validated in VRs against data
- [ ] Background-only fit in CRs converges, pulls < 1σ
- [ ] Expected limits match Asimov estimate within 10%
- [ ] Paper draft reviewed by physics group
- [ ] SR unblinded

---

## 10. Timeline and Milestones

| Milestone                  | Target date |
| -------------------------- | ----------- |
| NTuple production complete | YYYY-MM-DD  |
| CR/VR validation           | YYYY-MM-DD  |
| Results to physics group   | YYYY-MM-DD  |
| Paper submission           | YYYY-MM-DD  |
```

## Quality Checks

Before finalising `specification.md`:

- Every dataset container verified in AMI (not just assumed to exist)
- Every object WP has a corresponding CP tool and scale factor
- SR and all CRs are mutually orthogonal
- Each background has a method — "MC" alone is not a method unless normalized
  somewhere
- Systematics list covers all objects used in the analysis
