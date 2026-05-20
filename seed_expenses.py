import sys
import random
from datetime import datetime, timedelta
from Database.db import get_db

CATEGORIES = {
    "Food": {"min": 10, "max": 800, "weight": 30},
    "Bill": {"min": 50, "max": 500, "weight": 20},
    "Transport": {"min": 5, "max": 100, "weight": 15},
    "Health": {"min": 100, "max": 5000, "weight": 5},
    "Entertainment": {"min": 0, "max": 300, "weight": 5},
    "Shopping": {"min": 10, "max": 1000, "weight": 15},
    "Other": {"min": 50, "max": 1000, "weight": 10},
}

DESCRIPTIONS = {
    "Food": ["Restaurant dinner", "Grocery shopping", "Coffee", "Lunch with colleagues", "Food delivery", "Bakery items", "Breakfast", "Snacks", "Takeaway", "Supermarket run"],
    "Bill": ["Electricity bill", "Water bill", "Gas bill", "Internet bill", "Phone bill", "Rent payment", "Insurance", "TV subscription", "Council tax", "Maintenance fee"],
    "Transport": ["Bus fare", "Taxi ride", "Train ticket", "Fuel", "Parking fee", "Metro card", "Uber", "Car wash", "Bike repair", "Flight booking"],
    "Health": ["Pharmacy", "Doctor appointment", "Dental checkup", "Vitamin supplements", "Hospital visit", "Eye test", "Therapy session", "Health insurance", "Medical test", "Gym membership"],
    "Entertainment": ["Movie tickets", "Concert", "Streaming subscription", "Gaming", "Bowling", "Theme park", "Bar", "Club night", "Festival", "KTV"],
    "Shopping": ["Clothes", "Electronics", "Shoes", "Accessories", "Home decor", "Furniture", "Beauty products", "Books", "Gifts", "Online order"],
    "Other": ["Miscellaneous", "Pet supplies", "Charity donation", "Fine", "Repair", "Subscription", "Renewal", "Fees", "Tip", "Other expense"]
}

def parse_args():
    if len(sys.argv) != 4:
        print("Usage: /seed-expenses <user_id> <count> <months>\nExample: /seed-expenses 1 50 6")
        sys.exit(1)
    
    try:
        user_id = int(sys.argv[1])
        count = int(sys.argv[2])
        months = int(sys.argv[3])
    except ValueError:
        print("Usage: /seed-expenses <user_id> <count> <months>\nExample: /seed-expenses 1 50 6")
        sys.exit(1)
    
    return user_id, count, months

def generate_expenses(user_id, count, months):
    today = datetime.now()
    start_date = today - timedelta(days=months * 30)
    
    category_list = []
    for cat, props in CATEGORIES.items():
        category_list.extend([cat] * props["weight"])
    
    expenses = []
    for _ in range(count):
        category = random.choice(category_list)
        props = CATEGORIES[category]
        amount = round(random.uniform(props["min"], props["max"]), 2)
        
        days_offset = random.randint(0, months * 30)
        date = (start_date + timedelta(days=days_offset)).strftime("%Y-%m-%d")
        
        description = random.choice(DESCRIPTIONS[category])
        
        expenses.append((user_id, amount, category, date, description))
    
    expenses.sort(key=lambda x: x[3])
    return expenses

def insert_expenses(user_id, expenses):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    if cursor.fetchone() is None:
        conn.close()
        raise ValueError(f"User with id {user_id} does not exist")
    
    try:
        cursor.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            expenses
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        conn.close()
        raise e
    
    conn.close()
    return len(expenses)

def main():
    user_id, count, months = parse_args()
    
    if count <= 0:
        print("Error: count must be greater than 0")
        sys.exit(1)
    
    expenses = generate_expenses(user_id, count, months)
    inserted = insert_expenses(user_id, expenses)
    
    date_range = f"{expenses[0][3]} to {expenses[-1][3]}"
    
    print(f"\n{inserted} expenses inserted")
    print(f"Date range: {date_range}")
    print("\nSample of 5 inserted records:")
    for exp in expenses[:5]:
        print(f"  {exp[3]} | {exp[2]} | £{exp[1]:.2f} | {exp[4]}")

if __name__ == "__main__":
    main()