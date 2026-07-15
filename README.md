# Inventory Manager

Offline desktop application for **Army Non-CSD canteen** vendor and product management.

## Run on Linux (development)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

Uses **PySide6** via `utils/qt.py`. Fully offline with a local SQLite file.

## Windows 8 offline USB deploy (end-user executable)

**Latest usable Python for the build PC: 3.10.11**  
(Python 3.11+ cannot install PySide2; PySide6/Qt6 cannot run on Windows 8.)

### Build once (Windows PC with internet)

1. Install [Python 3.10.11 64-bit](https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe) — tick **Add to PATH**, then open a **new** Command Prompt.
2. Double-click **`BUILD_WINDOWS8.bat`** (does **not** need Administrator).
   - Window stays open on success or failure; full log is written to `build_log.txt`.
   - If the window still flashes away, use **`BUILD_WINDOWS8_KEEP_OPEN.bat`** instead.
3. Copy `dist\InventoryManager\` onto USB.

### Run on Windows 8 (no Python, no internet)

Double-click **`InventoryManager.exe`** (or `START_HERE.bat`).  
If launch fails, open `logs\startup.log` next to the exe.

| Target | Qt binding | Requirements | Python on build PC |
|--------|------------|--------------|--------------------|
| Linux / Win10+ dev | PySide6 | `requirements.txt` | 3.10+ |
| Windows 8 packaged | PySide2 5.15 | `requirements-win8.txt` | **3.8–3.10** (prefer **3.10.11**) |

UI code imports only from `utils.qt`, which auto-selects the available binding. The frozen USB folder embeds Python + Qt — the Win8 PC needs neither installed.

## Architecture

MVC + Repository + Service — only the UI depends on Qt:

| Layer | Role |
|-------|------|
| `views/` | Screens (via `utils.qt`) |
| `controllers/` | Wire UI → services |
| `services/` | Validation and business rules |
| `repositories/` | SQLAlchemy / SQLite |
| `models/` | ORM entities + DTOs |
| `database/` | Engine, schema, seed data |
| `packaging/` | PyInstaller Win8 build |

Paths resolve from the app folder (`utils.paths.get_app_root`) so USB / any drive letter works.
