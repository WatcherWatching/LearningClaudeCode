# Spec: Login and Logout

## Overview
Step 3 implements user login and logout functionality for the Spendly application. Building on the user registration system from Step 2, this step adds secure authentication mechanisms including session management, password verification, and route protection. Users can now securely log in with their credentials and log out when finished, establishing the foundation for personalized features like profile management and expense tracking.

## Depends on
- Step 1 – Database setup (get_db, init_db, seed_db, users table)
- Step 2 – Registration system (create_user helper, POST /register handling)

## Routes
- GET /login – renders login.html – public
- POST /login – validates credentials, creates session, redirects to profile – public
- GET /logout – clears session, redirects to landing – logged-in

## Database changes
No database changes required. The existing users table from Step 1 contains all necessary fields (id, name, email, password_hash, created_at) for authentication.

## Templates
- Create: none
- Modify:
  - templates/login.html – form action should use url_for('login'), add proper input fields for email and password
  - templates/base.html – add conditional navigation links based on authentication state (show login/register when logged out, show profile/logout when logged in)

## Files to change
- app.py – implement login route with GET and POST handlers, implement logout route, add session management, add helper function for checking authentication status
- database/db.py – add get_user_by_email helper function to retrieve user by email for authentication
- templates/login.html – update form to use url_for('login') and proper field names
- templates/base.html – add conditional navigation based on user authentication state

## Files to create
- None

## New dependencies
- flask.session for session management (already included with Flask)
- No new pip packages required

## Rules for implementation
- No SQLAlchemy or ORMs – use raw sqlite3 only
- All SQL must use parameterized queries with ? placeholders – never f-strings in SQL
- Passwords must be verified using werkzeug.security.check_password_hash
- Use Flask sessions for authentication state management
- Set session permanent=False for security
- Use secure session cookies in production (though not required for development)
- DB logic must live in database/db.py – route functions only call helpers
- Use abort() for HTTP errors where appropriate
- All templates must extend base.html
- All template links must use url_for() – never hardcode URLs
- Use CSS variables from static/css/style.css for any new styles – never hardcode hex values
- Route functions should be single-responsibility: process request → call helper → redirect/render
- Implement proper error handling for invalid credentials
- On successful login, redirect to profile page with success indicator
- On logout, clear session and redirect to landing page
- Session should store user ID and optionally user name for template access

## Definition of done
- [ ] GET /login continues to render login.html unchanged
- [ ] POST /login with valid credentials creates a user session and redirects to /profile
- [ ] POST /login with invalid email re-renders login form with error message
- [ ] POST /login with invalid password re-renders login form with error message
- [ ] GET /logout clears the user session and redirects to /
- [ ] After logout, accessing /profile redirects to login page (or shows appropriate error)
- [ ] Base template shows login/register links when user is logged out
- [ ] Base template shows profile/logout links when user is logged in
- [ ] User name is available in templates when logged in
- [ ] Passwords are verified using werkzeug.security.check_password_hash, never compared plaintext
- [ ] All database access in login/logout flows uses parameterized queries
- [ ] App starts without errors and existing test suite still passes
- [ ] Sessions are properly invalidated on logout