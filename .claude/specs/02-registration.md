# Spec: Registration

## Overview
Step 2 implements user registration on top of the database layer established in Step 1. The `/register` route currently only renders `register.html`; this step wires up `POST` handling so a new user can submit name, email, and password and have their account persisted (with a hashed password) to the `users` table. After successful registration,the user is shown with a success message and then the user is redirected to `/login` with a success indicator so they can sign in. Server-side validation, duplicate-email handling, and password hashing with `werkzeug.security` are the core concerns — login and session management are deliberately out of scope and will be addressed in Step 3.

## Depends on
- Step 1 – Database setup (`get_db`, `init_db`, `seed_db`, `users` table with `UNIQUE` email)

## Routes
- `GET /register` – renders `register.html` – public
- `POST /register` – validates form, creates user, redirects to `/login?registered=1` – public

## Database changes
No database changes. The `users` table from Step 1 already has the columns this step needs (`name`, `email`, `password_hash`, `created_at`).

A new DB helper must be added to `database/
db.py`:
- `create_user(name, email, password)` –
hashes the password with `werkzeug`,
inserts a row into `users`, returns the new
user's `id`. Raises `sqlite3.
IntegrityError` if the email is already
taken (UNIQUE constraint).

## Templates
- Create: none
- Modify:
  - `templates/register.html` – form `action` currently hardcoded to `/register`; switch to `{{ url_for('register') }}`. Confirm `name` attribute values stay as `name`, `email`, `password`.

## Files to change
- `app.py` – add `request` import, add new DB helper `create_user` callsite usage, convert `/register` to handle both GET and POST, add validation and hashing
- `database/db.py` – add `create_user(name, email, password_hash) -> int` helper that inserts a user and returns the new id
- `templates/register.html` – replace hardcoded `/register` action with `url_for('register')`

## Files to create
None

## New dependencies
No new dependencies. `werkzeug.security.generate_password_hash` is already available (used in `seed_db`).

## Rules for implementation
- No SQLAlchemy or ORMs — raw `sqlite3` only
- All SQL must use parameterized queries with `?` placeholders — never f-strings in SQL
- Passwords must be hashed with `werkzeug.security.generate_password_hash` before storage — never store plaintext
- DB logic must live in `database/db.py` — route functions only call helpers
- Use `abort(400)` / `abort(409)` for HTTP errors where appropriate; do not return raw error strings
- All templates extend `base.html`
- All template links use `url_for()` — never hardcode URLs
- Use CSS variables defined in `static/css/style.css` for any new styles — never hardcode hex values
- Route functions should be single-responsibility: read form → call helper → flash/redirect/render
- The current `register.html` already expects an `error` variable in the template context for inline error display — preserve that contract
- Email comparison for duplicate detection must be case-insensitive (normalize to lowercase before insert and before lookup)
- Validation rules:
  - `name`: required, stripped, 1–80 chars
  - `email`: required, must contain `@` and `.`, normalized to lowercase
  - `password`: required, minimum 8 characters
- On success: redirect with `302` to `url_for('login', registered=1)`
- On failure: re-render `register.html` with `error` set and HTTP `400` (use `render_template` with status code via the `abort` flow is acceptable, but a simple re-render with `error` is cleaner — pick re-render)

## Definition of done
- [ ] `GET /register` continues to render `register.html` unchanged
- [ ] `POST /register` with valid data creates a new row in `users` (verifiable via `sqlite3 spendly.db "SELECT * FROM users"`)
- [ ] The stored `password_hash` is a werkzeug hash, not the plaintext password
- [ ] `POST /register` with an already-registered email re-renders the form with an error message and does NOT create a duplicate row
- [ ] `POST /register` with a password under 8 characters re-renders with an error
- [ ] `POST /register` with an invalid email (no `@`/`.`) re-renders with an error
- [ ] `POST /register` with empty `name` re-renders with an error
- [ ] On success, the browser is redirected to `/login?registered=1` (verifiable via the redirect status and URL)
- [ ] `create_user` lives in `database/db.py` and uses a parameterized `INSERT`
- [ ] `app.py` contains no raw SQL — all DB access is via helpers
- [ ] `templates/register.html` no longer contains a hardcoded `/register` action
- [ ] App starts without errors and `pytest` still runs the existing suite
