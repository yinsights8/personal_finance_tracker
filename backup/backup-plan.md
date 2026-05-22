# Backup Plan — personal_finance_tracker

## What Needs Backup

### Already in Git (safe with remote push)
- All source code: `app.py`, `test.py`, `Database/`, `Schemas/`
- Templates: `templates/` (3 files)
- Static assets: `static/` (4 files)
- Documentation: `README.md`, `AGENTS.md`, `plans/`, `implimented_plans/`

### NOT in Git — Must Save Separately
| File | Why | Size |
|------|-----|------|
| `.env` | SECRET_KEY, DB name — gitignored | ~100 B |
| `expense_tracker.db` | All user data — gitignored via `*.db` | ~32 KB |
| `requirements.txt` | Exact pinned dependencies — untracked | ~1.3 KB |

## Backup Strategy

### 1. Git → GitHub (source code)
```bash
git push origin main
```

### 2. Local archive (data + secrets)
Run `.\backup.ps1` which creates a dated zip in `backup/`:
```
backup/backup_2026-05-22_103000.zip
  ├── .env
  ├── expense_tracker.db
  └── requirements.txt
```

## Restoration Procedure

```bash
# 1. Clone source code
git clone <repo-url>
cd personal_finance_tracker

# 2. Restore secrets & data from backup
#    Extract latest backup_*.zip from backup/ into project root

# 3. Set up virtual environment
python -m venv .venv
.venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run
python app.py
```

## Quick Backup (end of session)
```powershell
.\backup.ps1; git push
```
