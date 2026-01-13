# Backend Setup

## Prerequisites

- Python 3.11+
- Virtual environment tool (venv, pipenv, etc.)

## Install dependencies

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Environment variables

Copy `.env.example` to `.env` and adjust values if needed.

```powershell
Copy-Item .env.example .env
```

## Initialize Database and Accounts

First, run the migration to add role column (if needed):

```powershell
python scripts/migrate_add_role.py
```

Then, initialize admin account:

```powershell
python scripts/init_admin.py
```

This will create:
- **Admin account**: `admin@ggzj.edu` / `admin123456`

To create a teacher account:

```powershell
python scripts/init_admin.py --teacher-email teacher@example.com --teacher-nickname "Teacher Name" --teacher-password teacher123456
```

**Note**: Students can register through the frontend registration page. Teachers must be created by admin.

## Run API

```powershell
python run.py
```

The API will be available at `http://127.0.0.1:8000`.

You can also use Flask's CLI:

```powershell
flask --app app.main:create_app run --debug
```

## Default Accounts

After initialization, you can use these accounts for testing:

- **Admin**: `admin@ggzj.edu` / `admin123456`
- **Teacher** (if created): `teacher@ggzj.edu` / `teacher123456`
- **Student**: Register through the frontend registration page

