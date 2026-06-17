"""Seed a user with realistic Indian expense data spread across recent months."""

import random
from datetime import date, timedelta

from database.db import get_db

# (category, weight, min_amount, max_amount, [descriptions])
CATEGORIES = [
    ("Food", 28, 50, 800, [
        "Chai and samosa", "Veg thali at Murugan Idli Shop", "Dominos pizza",
        "Bigbasket groceries", "Subway veggie delite", "Biryani at Paradise",
        "Dosa and filter coffee", "MTR breakfast", "Swiggy order", "Zomato dinner",
        "Maggi and pakoda", "Street food platter", "Local mess lunch",
        "Sambar rice", "Curd rice", "Fresh fruits from Reliance Fresh",
        "Bread, butter, jam", "Amul butter and Parle-G", "Cafe Coffee Day",
        "Chai tapri", "Idli vada sambar", "Pav bhaji at Sardar",
    ]),
    ("Transport", 22, 20, 500, [
        "Uber to office", "Ola auto", "Rapido bike ride", "BMTC bus pass top-up",
        "Metro card recharge", "Petrol refill", "Auto rickshaw to station",
        "Namma Metro QR ticket", "Uber Cab to airport", "Diesel for car",
        "State transport bus", "BMTC day pass", "Local train ticket",
        "VRL Travels sleeper", "SRS Travels AC", "Parking charges at mall",
        "Toll booth NHAI", "Cab to airport T2",
    ]),
    ("Bills", 14, 200, 3000, [
        "BESCOM electricity bill", "Jio postpaid mobile", "Airtel broadband",
        "Apartment maintenance", "Tata Sky DTH recharge", "ACT Fibernet",
        "BSNL landline", "BWSSB water bill", "Gas cylinder refill",
        "Piped gas PNG bill", "DTH recharge for Sony LIV", "Insurance premium",
        "Credit card bill payment", "Municipal corporation tax", "LIC premium",
    ]),
    ("Health", 6, 100, 2000, [
        "Apollo Pharmacy medicines", "Practo doctor consultation",
        "Diagnostics blood test", "HealthKart protein",
        "Pharmacy near home", "Dental check-up at Clove Dental",
        "Eye checkup at Sankara", "Vitamin supplements",
        "First aid supplies", "Co-vid booster",
    ]),
    ("Entertainment", 7, 100, 1500, [
        "PVR Inox movie tickets", "Netflix subscription", "Amazon Prime renewal",
        "Spotify Premium", "BookMyShow concert", "Wonderla day pass",
        "Disney+ Hotstar annual", "Audible India subscription",
        "PVR gold class", "Gaming top-up Steam",
    ]),
    ("Shopping", 15, 200, 5000, [
        "Amazon.in order - headphones", "Flipkart Big Billion Days",
        "Myntra clothing", "Ajio kurta purchase", "Nykaa cosmetics",
        "Decathlon sports shoes", "Croma electronics", "Reliance Digital",
        "Lifestyle store shirt", "Pantaloons jeans", "IKEA Hyderabad",
        "Local tailor stitching", "Amazon Pay UPI cashback offer",
    ]),
    ("Other", 8, 50, 1000, [
        "Haircut at Lakme Salon", "Tailor alterations", "Bus ticket to Mysuru",
        "IRCTC Tatkal train ticket", "Domestic flight SpiceJet",
        "Hotel stay for wedding", "Gift wrap and card", "Donation to temple",
        "Laundry dhobi", "House help salary", "Maid service",
        "Pooja items", "Car wash",
    ]),
]

# Indian-context descriptions already encoded in CATEGORIES above.


def generate(user_id: int, count: int, months: int) -> list[tuple]:
    """Build `count` expense rows spread across the past `months` months."""
    today = date.today()
    # Earliest day: first-of-(months-1)-ago -> we want a span of `months` distinct months,
    # so earliest = first of the month `months - 1` calendar months before today.
    first_of_current = today.replace(day=1)
    earliest_month_start = first_of_current
    for _ in range(months - 1):
        prev = earliest_month_start - timedelta(days=1)
        earliest_month_start = prev.replace(day=1)

    # Total days from earliest_month_start to today inclusive
    span_days = (today - earliest_month_start).days
    if span_days <= 0:
        span_days = 1

    weights = [c[1] for c in CATEGORIES]
    categories = [c[0] for c in CATEGORIES]
    bounds = {c[0]: (c[2], c[3]) for c in CATEGORIES}
    descs = {c[0]: c[4] for c in CATEGORIES}

    rows = []
    for _ in range(count):
        category = random.choices(categories, weights=weights, k=1)[0]
        lo, hi = bounds[category]
        amount = round(random.uniform(lo, hi), 2)
        offset = random.randint(0, span_days)
        expense_date = (earliest_month_start + timedelta(days=offset)).isoformat()
        description = random.choice(descs[category])
        rows.append((user_id, amount, category, expense_date, description))
    return rows


def main(user_id: int, count: int, months: int):
    rows = generate(user_id, count, months)

    conn = get_db()
    try:
        # Re-verify user exists inside the same transaction context.
        user = conn.execute(
            "SELECT id FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        if user is None:
            print(f"No user found with id {user_id}.")
            return

        try:
            conn.execute("BEGIN")
            conn.executemany(
                "INSERT INTO expenses (user_id, amount, category, date, description) "
                "VALUES (?, ?, ?, ?, ?)",
                rows,
            )
            conn.commit()
        except Exception as exc:
            conn.rollback()
            print(f"Insert failed, rolled back: {exc}")
            return

        # Fetch the rows we just inserted. Bound the query to the date window
        # we generated, so any pre-existing expenses for this user don't sneak in.
        min_date = min(r[3] for r in rows)
        inserted = conn.execute(
            "SELECT id, user_id, amount, category, date, description "
            "FROM expenses WHERE user_id = ? AND date >= ? "
            "ORDER BY date ASC, id ASC",
            (user_id, min_date),
        ).fetchall()
        # Take only the last `count` — they are the ones we just wrote
        # (highest AUTOINCREMENT ids).
        inserted = inserted[-count:]

        dates = [r["date"] for r in inserted]
        print(f"Inserted {len(inserted)} expenses for user_id={user_id}.")
        print(f"Date range: {min(dates)}  to  {max(dates)}")
        print("Sample (5 records):")
        for r in inserted[:5]:
            print(f"  #{r['id']:>3}  {r['date']}  {r['category']:<14} "
                  f"Rs.{r['amount']:>8.2f}  {r['description']}")
    finally:
        conn.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 4:
        print("Usage: /seed-expenses <user_id> <count> <months>")
        print("Example: /seed-expenses 1 50 6")
        sys.exit(1)

    try:
        user_id = int(sys.argv[1])
        count = int(sys.argv[2])
        months = int(sys.argv[3])
    except ValueError:
        print("Usage: /seed-expenses <user_id> <count> <months>")
        print("Example: /seed-expenses 1 50 6")
        sys.exit(1)

    main(user_id, count, months)
