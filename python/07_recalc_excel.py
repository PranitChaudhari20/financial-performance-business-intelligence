"""
07_recalc_excel.py  -  write cached values into the Excel workbook
==================================================================
Author: Pranit Ajay Chaudhari

openpyxl writes formulas as text and cannot evaluate them, so a workbook it has just generated has
no cached results. Anything that reads cached values - pandas, `load_workbook(data_only=True)`,
GitHub's file preview, Google Drive's preview, and this project's own `06_verify.py` - sees every
formula cell as empty, and the workbook looks blank even though the formulas are correct.

This step hands the file to LibreOffice, which evaluates every formula and writes the results back.
It needs only `soffice` on PATH - no environment-specific paths - so it works on any machine with
LibreOffice installed. If LibreOffice is absent it says so clearly and exits 0 WITHOUT claiming to
have recalculated anything: the workbook is still valid, and opening it once in Excel and saving
has the same effect. `06_verify.py` then reports its Excel checks as NOT RUN rather than failing,
so "could not verify" is never confused with "verified and wrong".

Run:  python python/07_recalc_excel.py
"""
import shutil
import subprocess
import sys
import tempfile
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
XL = ROOT / "excel" / "Financial_Performance_Analytics.xlsx"
ERRORS = {"#DIV/0!", "#N/A", "#NAME?", "#NULL!", "#NUM!", "#REF!", "#VALUE!", "#SPILL!", "#CALC!"}


def report(path, label):
    wf = load_workbook(path)
    wv = load_workbook(path, data_only=True)
    n = cached = blank = errs = 0
    bad = []
    for sheet in wf.sheetnames:
        a, b = wf[sheet], wv[sheet]
        for row in a.iter_rows():
            for cell in row:
                if isinstance(cell.value, str) and cell.value.startswith("="):
                    n += 1
                    v = b.cell(cell.row, cell.column).value
                    if v is None:
                        blank += 1
                    elif isinstance(v, str) and v in ERRORS:
                        errs += 1
                        bad.append(f"{sheet}!{cell.coordinate}={v}")
                    else:
                        cached += 1
    print(f"  {label}: {n} formulas, {cached} cached, {blank} blank, {errs} errors")
    return n, cached, blank, errs, bad


def main():
    if not XL.exists():
        print(f"  {XL.relative_to(ROOT)} not found - run python/05_build_excel.py first.")
        return 1

    report(XL, "before")

    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        print("\n  LibreOffice (soffice) is NOT installed, so the formulas were NOT recalculated.")
        print("  The workbook is still valid: open it once in Excel or LibreOffice and save, and")
        print("  every value appears. Until then python/06_verify.py reports its Excel checks as")
        print("  NOT RUN (exit code 2) rather than as a failure.")
        return 0

    # A LibreOffice run that was interrupted leaves a .~lock file beside the workbook, and every
    # later attempt to open that path then blocks on it until it times out. Clear it first.
    for lock in XL.parent.glob(".~lock.*"):
        lock.unlink()
        print(f"  removed stale lock file {lock.name}")

    with tempfile.TemporaryDirectory() as tmp:
        proc = subprocess.run(
            [soffice, "--headless", "--norestore", "--convert-to", "xlsx", "--outdir", tmp, str(XL)],
            capture_output=True, text=True, timeout=900)
        out = Path(tmp) / XL.name
        if proc.returncode != 0 or not out.exists():
            print(f"\n  LibreOffice could not convert the file (exit {proc.returncode}).")
            print(f"  {(proc.stderr or proc.stdout or '').strip()[:300]}")
            print("  Open the workbook once in Excel and save instead.")
            return 0
        shutil.move(str(out), str(XL))

    for lock in XL.parent.glob(".~lock.*"):
        lock.unlink()

    n, cached, blank, errs, bad = report(XL, "after ")
    if errs:
        print(f"\n  {errs} formula cells evaluated to an error: {bad[:5]}")
        return 1
    if blank:
        print(f"\n  {blank} formula cells still have no cached value.")
        return 1
    print("\n  Every formula evaluated and cached. The workbook previews correctly on GitHub.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
