# Inventory Manager

Offline desktop application for **Army Non-CSD canteen** vendor and product management.

## Run on Linux (development)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

Uses **PySide6** via `utils/qt.py`. Works fully offline with a local SQLite file.

## Windows 8 offline USB deploy

Build on a Windows PC with **Python 3.8–3.10** (not 3.11+):

```bat
py -3.9 -m venv venv
venv\Scripts\activate
pip install -r requirements-win8.txt
packaging\build_windows.bat
```

Copy `dist\InventoryManager\` to USB and double-click `InventoryManager.exe`.
If launch fails, check `logs\startup.log`.

| Target | Qt binding | Requirements file |
|--------|------------|-------------------|
| Linux / Win10+ dev | PySide6 | `requirements.txt` |
| Windows 8 packaged | PySide2 5.15 | `requirements-win8.txt` |

UI code imports only from `utils.qt`, which auto-selects the available binding.

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

Paths resolve from the app folder (`utils.paths.get_app_root`) so USB/any drive letter works.
