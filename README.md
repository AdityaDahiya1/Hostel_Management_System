# Hostel_Management_System


This project is a small, self-contained hostel management system written in Python using Tkinter for the UI and SQLite for data storage.

**Features**
- Student registration, update, delete, search
- Room creation and allocation (simple capacity check)
- Fee recording and simple reports
- Export students list to CSV
- Simple, single-file runnable GUI (plus optional DB init)

**Files in this project**
- requirements.txt
- README.md (this file)
- db_init.py (create DB and tables)
- models.py (database access layer)
- main.py (Tkinter GUI application — run this)
- utils.py (helper functions)

**Requirements**
- Python 3.8+
- No third-party packages required. (optionally: pillow)

**How to run**
1. (Optional) Create a virtual environment:
   python -m venv venv
   source venv/bin/activate  # linux/mac
   venv\\Scripts\\activate   # windows

2. Initialize the database (optional — main.py will auto-init if missing):
   python db_init.py

3. Run the GUI:
   python main.py
