---
name: cds-fetch
description: Fetch documents from the CERN Document Server (CDS, cds.cern.ch), which is behind the Anubis anti-bot gate. Use whenever the user gives a cds.cern.ch record or file URL, or when an ordinary web fetch of CDS returns a "Making sure you're not a bot!" page instead of the record. Works for any experiment (ATLAS, CMS, general CERN notes).
---

# CDS Fetch

## Overview

The CERN Document Server (`cds.cern.ch`) sits behind **Anubis**, a proof-of-work
anti-bot gate. An ordinary HTTP client — `curl`, `wget`, or a web-fetch tool —
receives HTTP 200 but a "Making sure you're not a bot!" interstitial, not the
record. Do **not** try to read CDS with a plain web-fetch tool; use the bundled
script, which performs the same lightweight proof-of-work a browser would,
caches the clearance cookie, and returns the real page or file.

## Workflow

1. Run the bundled script on the CDS URL (requires [`uv`](https://docs.astral.sh/uv/)):

   ```bash
   uv run --script assets/cds_fetch.py <cds-url> [output-file]
   ```

   - Record page to a file:
     `uv run --script assets/cds_fetch.py https://cds.cern.ch/record/2928097/ record.html`
   - Attached PDF:
     `uv run --script assets/cds_fetch.py https://cds.cern.ch/record/2928097/files/NOTE2025_007.pdf paper.pdf`
   - Omit the output file to stream to stdout (pipe into a parser).

2. To find a record's attached files, fetch the record page and look for
   `/record/<id>/files/` links, then fetch those.

3. Read the returned HTML/PDF as usual.

The first fetch solves the proof-of-work (difficulty 4 ≈ 40k SHA-256 iterations,
under a second) and caches the `techaro.lol-anubis-auth` cookie in
`~/.cache/cds-anubis/` for ~3 hours. Subsequent fetches reuse the cookie and
skip the proof-of-work.

## Requirements

- `uv` is used to run the single-file script; it installs the one dependency
  (`typer`) automatically. The proof-of-work itself uses only the standard
  library.
- The script clears the **bot gate only**. Genuinely access-restricted CDS
  records still require CERN SSO — it cannot and does not bypass authentication.
- If CERN upgrades Anubis and changes the challenge scheme, the solver may need
  updating; check the `anubis_challenge` JSON embedded in the interstitial page.

## Assets

- `assets/cds_fetch.py` — PEP 723 single-file script (`uv run --script`) that
  solves the Anubis proof-of-work, caches the cookie, and fetches a CDS URL.
