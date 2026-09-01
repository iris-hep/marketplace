#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = ["typer"]
# ///
"""Fetch documents from the CERN Document Server (CDS).

CDS sits behind Anubis, a proof-of-work anti-bot gate: an ordinary HTTP client
receives a "Making sure you're not a bot!" interstitial (HTTP 200) instead of
the record. This script performs the small proof-of-work the browser would run,
caches the resulting clearance cookie, and returns the real page or file.

    uv run --script cds_fetch.py https://cds.cern.ch/record/2928097/
    uv run --script cds_fetch.py https://cds.cern.ch/record/2928097/files/NOTE2025_007.pdf paper.pdf
"""
import hashlib
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from http.cookiejar import MozillaCookieJar
from typing import Optional

import typer

UA = "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"
CACHE = os.path.expanduser("~/.cache/cds-anubis/cookies.txt")
CDS_HOST = "cds.cern.ch"
ANUBIS_PASS = f"https://{CDS_HOST}/.within.website/x/cmd/anubis/api/pass-challenge"
HTTP_TIMEOUT = 30  # seconds; no single network call should hang longer than this
MAX_DIFFICULTY = 6  # refuse to grind absurd proof-of-work (each nibble is ~16x)


def check_url(url: str) -> None:
    """Restrict fetches to CDS over https (guards against SSRF and hostile challenges)."""
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != CDS_HOST:
        raise typer.BadParameter(f"URL must be https://{CDS_HOST}/... (got {url!r})")


def make_opener():
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    cj = MozillaCookieJar(CACHE)
    if os.path.exists(CACHE):
        cj.load(ignore_discard=True)
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    opener.addheaders = [("User-Agent", UA)]
    return opener, cj


def solve(random_data: str, difficulty: int):
    """Proof-of-work: increment a counter until sha256(random_data + counter)
    starts with `difficulty` leading zero nibbles; return the counter and digest."""
    target = "0" * difficulty
    counter = 0
    while True:
        digest = hashlib.sha256((random_data + str(counter)).encode()).hexdigest()
        if digest.startswith(target):
            return counter, digest
        counter += 1


def pass_challenge(opener, page_html: str, referer: str) -> None:
    match = re.search(r'id="anubis_challenge"[^>]*>(.*?)</script>', page_html, re.S)
    if match is None:
        raise RuntimeError(
            "no Anubis challenge found in the page; CDS markup may have changed"
        )
    c = json.loads(match.group(1))["challenge"]
    difficulty = int(c["difficulty"])
    if not 1 <= difficulty <= MAX_DIFFICULTY:
        raise RuntimeError(
            f"refusing Anubis challenge of difficulty {difficulty} (max {MAX_DIFFICULTY})"
        )
    started = time.time()
    counter, digest = solve(c["randomData"], difficulty)
    query = urllib.parse.urlencode(
        {
            "id": c["id"],
            "response": digest,
            "nonce": counter,  # Anubis names this proof-of-work field "nonce"
            "redir": referer,
            "elapsedTime": int((time.time() - started) * 1000),
        }
    )
    opener.open(ANUBIS_PASS + "?" + query, timeout=HTTP_TIMEOUT).read()


def fetch(
    url: str = typer.Argument(..., help="CDS record or file URL (https://cds.cern.ch/...)."),
    out: Optional[str] = typer.Argument(
        None, help="Write to this file instead of stdout."
    ),
) -> None:
    """Fetch a CDS page or file, solving the Anubis proof-of-work if required."""
    check_url(url)
    opener, cj = make_opener()
    data = opener.open(url, timeout=HTTP_TIMEOUT).read()
    # An Anubis interstitial is small HTML carrying the challenge script.
    if b"anubis_challenge" in data[:20000] and b"not a bot" in data[:2000]:
        pass_challenge(opener, data.decode("utf-8", "replace"), url)
        cj.save(ignore_discard=True)
        data = opener.open(url, timeout=HTTP_TIMEOUT).read()
    if out:
        with open(out, "wb") as handle:
            handle.write(data)
        typer.echo(f"wrote {len(data)} bytes -> {out}", err=True)
    else:
        sys.stdout.buffer.write(data)


if __name__ == "__main__":
    typer.run(fetch)
