"""Verify local thesis inputs before running dependency-heavy pipelines.

This module intentionally uses only the Python standard library so it can run even
before ``pip install -r requirements.txt`` succeeds.  It verifies the local data
archive, configured CSV names inside the archive or extracted tree, and required
document files, then writes a Markdown report with only observed facts.
"""
from __future__ import annotations

import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "configs" / "config.yaml"
RAW_DIR = ROOT / "data" / "raw"
DOCS_DIR = ROOT / "docs"
REPORT = ROOT / "results" / "reports" / "environment_verification.md"
EXPECTED_DOCS = ["s44333-024-00023-3 (1).pdf", "EV_Literature_Survey_Thesis_v2 (1).xlsx"]


def _configured_data_files() -> dict[str, str]:
    """Extract configured data filenames from config.yaml without PyYAML."""
    text = CONFIG.read_text(encoding="utf-8") if CONFIG.exists() else ""
    data_block = text.split("data:", 1)[1].split("target:", 1)[0] if "data:" in text and "target:" in text else ""
    files: dict[str, str] = {}
    for line in data_block.splitlines():
        match = re.match(r"\s*([a-zA-Z0-9_]+):\s*[\"']?([^\"'\n#]+?)[\"']?\s*(?:#.*)?$", line)
        if match:
            key, value = match.groups()
            if key.endswith("_file") or key.startswith("charger_hist_") or key == "zenodo_zip":
                files[key] = value.strip()
    return files


def _archive_members(zip_path: Path) -> set[str]:
    if not zip_path.exists() or zip_path.stat().st_size == 0:
        return set()
    with zipfile.ZipFile(zip_path, "r") as archive:
        return {Path(name).name for name in archive.namelist() if name.lower().endswith(".csv")}


def verify() -> bool:
    """Write environment verification report and return True if required inputs exist."""
    files = _configured_data_files()
    configured_zip = ROOT / files.get("zenodo_zip", "data/raw/13852045 (1).zip")
    candidate_zips = [configured_zip, *sorted(RAW_DIR.glob("13852045*.zip")), *sorted(RAW_DIR.glob("*.zip"))]
    local_zip = next((path for path in candidate_zips if path.exists() and path.stat().st_size > 0), configured_zip)
    extracted_csv_names = {path.name for path in RAW_DIR.glob("**/*.csv")}
    zip_csv_names = _archive_members(local_zip)
    available_csv_names = extracted_csv_names | zip_csv_names
    required_csvs = {key: value for key, value in files.items() if key != "zenodo_zip"}

    missing_csvs = {key: value for key, value in required_csvs.items() if Path(value).name not in available_csv_names}
    missing_docs = [name for name in EXPECTED_DOCS if not (DOCS_DIR / name).exists()]
    ok = local_zip.exists() and local_zip.stat().st_size > 0 and not missing_csvs and not missing_docs

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Environment Verification",
        "",
        "This report is generated from local filesystem checks only; it does not use external URLs.",
        "",
        "## Required local files",
        "",
        f"- Configured/local dataset archive: `{local_zip.relative_to(ROOT) if local_zip.is_relative_to(ROOT) else local_zip}` — {'present' if local_zip.exists() and local_zip.stat().st_size > 0 else 'missing'}",
    ]
    for doc in EXPECTED_DOCS:
        path = DOCS_DIR / doc
        lines.append(f"- `{path.relative_to(ROOT)}` — {'present' if path.exists() else 'missing'}")
    lines.extend(["", "## Required CSV availability", ""])
    for key, filename in required_csvs.items():
        status = "present" if Path(filename).name in available_csv_names else "missing"
        lines.append(f"- `{key}`: `{filename}` — {status}")
    lines.extend(["", "## Verification result", "", "PASS" if ok else "FAIL"])
    if missing_csvs or missing_docs or not (local_zip.exists() and local_zip.stat().st_size > 0):
        lines.extend(["", "## Blocking issues", ""])
        if not (local_zip.exists() and local_zip.stat().st_size > 0):
            lines.append("- The local dataset archive is absent or empty.")
        for key, filename in missing_csvs.items():
            lines.append(f"- Missing configured CSV `{key}`: `{filename}`.")
        for doc in missing_docs:
            lines.append(f"- Missing required document: `docs/{doc}`.")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(REPORT.relative_to(ROOT))
    print("PASS" if ok else "FAIL")
    return ok


if __name__ == "__main__":
    raise SystemExit(0 if verify() else 1)
