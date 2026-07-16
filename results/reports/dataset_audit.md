# Dataset Audit

Status: pending execution against downloaded Zenodo CSV files.

The audit generator is implemented in `src/preprocessing/audit_reports.py`. It downloads/extracts the Zenodo archive, loads every configured CSV, and writes dataset shape, null, dtype, and column summaries. This placeholder intentionally contains no fabricated dataset statistics because the archive was not reachable from the current environment.

Run:

```bash
python src/preprocessing/audit_reports.py
```
