---
phase: 7
plan: 1
wave: 1
---

# Plan 7.1: Backend Auth API Setup

## Objective
Establish the foundational authentication backend using Flask, SQLite (SQLAlchemy), Bcrypt, and PyJWT. This is required before the frontend can implement login views.

## Context
- .gsd/SPEC.md
- .gsd/ROADMAP.md
- .gsd/phases/7/RESEARCH.md

## Tasks

<task type="auto">
  <name>Install Backend Auth Dependencies</name>
  <files>requirements.txt</files>
  <action>
    Add `Flask-SQLAlchemy`, `Flask-Bcrypt`, `PyJWT`, and `Flask-Cors` (if not already present) to `requirements.txt`.
    Run `pip install -r requirements.txt`.
  </action>
  <verify>pip freeze | findstr Flask-SQLAlchemy</verify>
  <done>Dependencies successfully installed and documented.</done>
</task>

<task type="auto">
  <name>Create User Model</name>
  <files>src/models/user.py, src/app.py</files>
  <action>
    Define a SQLAlchemy `User` model with `id`, `username`, `email`, and `password_hash`.
    Initialize SQLAlchemy in `src/app.py` or a dedicated database module.
  </action>
  <verify>python -c "from src.app import db; print('DB Setup OK')"</verify>
  <done>User model defined and DB initializes without errors.</done>
</task>

<task type="auto">
  <name>Implement Auth Endpoints</name>
  <files>src/routes/auth_routes.py, src/app.py</files>
  <action>
    Create POST `/api/auth/register` (hashes password, saves user).
    Create POST `/api/auth/login` (verifies password, returns JWT).
    Register the blueprint in `src/app.py`.
  </action>
  <verify>python -c "import requests; print('Endpoint ready for testing')"</verify>
  <done>Valid JWT returned upon successful login.</done>
</task>

## Success Criteria
- [ ] Backend dependencies installed.
- [ ] SQLite database successfully creates the `User` table.
- [ ] `/api/auth/register` and `/api/auth/login` handle requests properly, returning a JWT on login.
