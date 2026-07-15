# Inventory Manager

Offline Windows desktop application for **Army Non-CSD canteen** vendor and product management.

## Windows 8 deployment (highest priority)

This project targets **Windows 8 (64-bit), fully offline, USB portable**.

| Component | Choice | Why |
|-----------|--------|-----|
| GUI | **PySide2 5.15** (Qt 5) | Qt 6 / PySide6 requires Windows 10+ |
| Database | SQLite + SQLAlchemy | No server, no internet |
| Packaging | PyInstaller one-folder | Double-click `.exe`, no Python install |

### Build the portable folder (on a Windows PC)

1. Install **Python 3.8, 3.9, or 3.10** (64-bit). Do **not** use 3.11+.
2. Open Command Prompt in the project folder:

```bat
py -3.9 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
packaging\build_windows.bat
```

3. Copy the entire output folder to USB:

```text
dist\InventoryManager\
    InventoryManager.exe
    platforms\          (contains qwindows.dll)
    styles\
    backups\
    logs\
    assets\
    icons\
    *.dll / Python runtime files
```

4. On the offline Windows 8 PC: double-click `InventoryManager.exe`.

If launch fails, open `logs\startup.log` on the USB drive — it records the failure reason.

### Run from source (developer machine)

```bash
# Requires Python 3.8–3.10 with PySide2 installed
python main.py
```

## Phase 1 features

- Vendor Management (CRUD, search, details)
- Product Management per vendor (CRUD, search, Excel-like grid)
- Local SQLite (`inventory.db` next to the exe)
- One-click Backup / Restore
- Logging under `logs/`

## Architecture

MVC + Repository + Service — UI is the only layer that depends on Qt:

| Layer | Role |
|-------|------|
| `views/` | PySide2 UI only |
| `controllers/` | Wire UI signals to services |
| `services/` | Validation and business rules |
| `repositories/` | SQLAlchemy / SQLite access |
| `models/` | ORM entities + DTOs |
| `database/` | Engine, schema, seed data |
| `config/` / `utils/` | Settings, paths, logging |
| `packaging/` | PyInstaller spec + Win8 build scripts |

All data paths resolve from the exe folder (`utils.paths.get_app_root`), so any drive letter (C:, D:, E:, USB) works.
