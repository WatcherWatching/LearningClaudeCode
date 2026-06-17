"""Seed a single realistic Indian user into the Spendly database."""
import random
import sys
from datetime import datetime
from pathlib import Path

# Make `database` importable when running from the project root.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from database.db import get_db  # noqa: E402
from werkzeug.security import generate_password_hash  # noqa: E402


# Realistic Indian first + last name pairs covering several regions.
INDIAN_NAMES = [
    ("Rahul", "Sharma"), ("Priya", "Verma"), ("Amit", "Patel"),
    ("Sneha", "Iyer"), ("Vikram", "Reddy"), ("Anjali", "Nair"),
    ("Rohit", "Gupta"), ("Pooja", "Joshi"), ("Arjun", "Khan"),
    ("Neha", "Kapoor"), ("Aditya", "Rao"), ("Kavya", "Menon"),
    ("Sandeep", "Singh"), ("Divya", "Pillai"), ("Karan", "Mehta"),
    ("Riya", "Chatterjee"), ("Manish", "Agarwal"), ("Sanya", "Malhotra"),
    ("Harsh", "Bhatia"), ("Tanvi", "Deshmukh"), ("Nikhil", "Banerjee"),
    ("Meera", "Saxena"), ("Varun", "Mishra"), ("Ishita", "Bhatt"),
    ("Saurabh", "Pandey"), ("Aishwarya", "Kulkarni"), ("Deepak", "Yadav"),
    ("Rashi", "Tiwari"), ("Mohit", "Chauhan"), ("Swati", "Srinivasan"),
]


def generate_email(first: str, last: str) -> str:
    """Build an email like rahul.sharma91@gmail.com with a 2-3 digit suffix."""
    suffix_length = random.randint(2, 3)
    suffix = "".join(random.choices("0123456789", k=suffix_length))
    # Make sure the suffix isn't all zeros — looks odd as a "user number".
    if suffix == "0" * suffix_length:
        suffix = suffix[:-1] + str(random.randint(1, 9))
    return f"{first.lower()}.{last.lower()}{suffix}@gmail.com"


def main() -> None:
    random.seed()
    conn = get_db()
    try:
        while True:
            first, last = random.choice(INDIAN_NAMES)
            name = f"{first} {last}"
            email = generate_email(first, last)
            existing = conn.execute(
                "SELECT 1 FROM users WHERE email = ?", (email,)
            ).fetchone()
            if not existing:
                break

        password_hash = generate_password_hash("password123")
        created_at = datetime.now().isoformat(sep=" ", timespec="seconds")

        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash, created_at) "
            "VALUES (?, ?, ?, ?)",
            (name, email, password_hash, created_at),
        )
        conn.commit()
        user_id = cursor.lastrowid

        print("User seeded successfully")
        print(f"  id:    {user_id}")
        print(f"  name:  {name}")
        print(f"  email: {email}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()