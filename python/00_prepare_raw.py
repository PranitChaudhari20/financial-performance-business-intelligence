"""
00_prepare_raw.py  -  privacy preparation of the raw file before it is committed
================================================================================
Author: Pranit Ajay Chaudhari

The Sample Superstore file carries a `Customer Name` column holding 793 full personal names. This
project is a FINANCIAL PERFORMANCE analysis: it measures revenue, cost, profit and margin by
product, category, region and period. It never analyses individual people, so the names are not
needed for a single figure in it, and shipping a column of personal names on a public repository
for no analytical purpose is not defensible.

`Customer ID` is kept because it is a pseudonymous key (e.g. `CG-12520`) and is needed to count
distinct customers for the revenue-concentration check. `Postal Code`, `City` and `State` are kept
because regional performance is one of the required analyses, and a postal code without a name or
street address does not identify a household.

The script is idempotent, re-scans afterwards, and refuses to pass if any obvious personal
identifier remains. It is a one-time preparation step, not part of run_all.sh.

Run:  python python/00_prepare_raw.py
"""
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "sample_superstore.csv"

DROP = ["Customer Name"]
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE = re.compile(r"(?<!\d)(?:\+?\d{1,3}[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}(?!\d)")


def scan(path):
    """Scan CELL VALUES, not the raw file text.

    Scanning the file as one string produces false positives across line breaks: a Sales value
    ending one row (`100.122`) runs into the next row's Row ID (`1159`) and the pair looks like a
    phone number. A first version of this script reported 364 such 'phone numbers', every one of
    them an artefact of the newline. Matching per cell removes that entire class of error.
    """
    df = pd.read_csv(path, encoding="latin-1", dtype=str, keep_default_na=False)
    emails, phones = set(), set()
    for col in df.columns:
        values = df[col].astype(str)
        for v in values[values.str.contains(EMAIL, regex=True, na=False)].unique():
            emails.add(f"{col}: {v}")
        for v in values[values.str.contains(PHONE, regex=True, na=False)].unique():
            phones.add(f"{col}: {v}")
    return {"emails": sorted(emails), "phones": sorted(phones)}


def main():
    if not RAW.exists():
        print(f"  {RAW} not found. See data/raw/README.md for how to obtain it.")
        return 1

    df = pd.read_csv(RAW, encoding="latin-1")
    print(f"  loaded {len(df):,} rows x {df.shape[1]} columns")

    present = [c for c in DROP if c in df.columns]
    if present:
        n_names = df[present[0]].nunique()
        df = df.drop(columns=present)
        df.to_csv(RAW, index=False, encoding="utf-8")
        print(f"  removed {present} - {n_names} distinct personal names")
    else:
        print(f"  {DROP} already removed (nothing to do)")

    found = scan(RAW)
    print(f"  remaining columns ({df.shape[1]}): {list(df.columns)}")
    print(f"\n  email addresses in the file : {len(found['emails'])}")
    print(f"  phone-shaped strings        : {len(found['phones'])}")
    if found["emails"] or found["phones"]:
        print("  Personal data still present - do not publish.")
        return 1
    if any(c in df.columns for c in DROP):
        print("  Name column still present - do not publish.")
        return 1
    print("\n  Clean. Safe to commit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
