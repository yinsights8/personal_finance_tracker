import random
from datetime import datetime
from werkzeug.security import generate_password_hash
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Database.db import get_db

FIRST_NAMES = {
    "North": ["Amit", "Rahul", "Vikram", "Priya", "Neha", "Sanjay", "Anita", "Raj", "Meera", "Deepak"],
    "South": ["Arun", "Karthik", "Lakshmi", "Divya", "Suresh", "Madhavi", "Ravi", "Sowmya", "Ganesh", "Kavya"],
    "East": ["Sourav", "Priyanka", "Debasis", "Mousumi", "Rajat", "Shreya", "Indrajit", "Bhoomi", "Subhash", "Ankita"],
    "West": ["Akshay", "Pooja", "Vishal", "Ankita", "Sagar", "Rashmi", "Nikhil", "Snehal", "Amitabh", "Shweta"]
}

LAST_NAMES = {
    "North": ["Sharma", "Gupta", "Verma", "Kumar", "Singh", "Patel", "Khanna", "Mehta", "Joshi", "Bhatia"],
    "South": ["Rao", "Naidu", "Reddy", "Pillai", "Menon", "Nair", "Iyer", "Krishnan", "Subramanian", "Choudhary"],
    "East": ["Das", "Mukherjee", "Banerjee", "Sengupta", "Chatterjee", "Bandyopadhyay", "Ghosh", "Sinha", "Ray", "Mondal"],
    "West": ["Shah", "Patil", "Deshmukh", "Kulkarni", "Joshi", "Sawant", "Mhatre", "Kamble", "Desai", "Trivedi"]
}

def generate_unique_user():
    region = random.choice(["North", "South", "East", "West"])
    first_name = random.choice(FIRST_NAMES[region])
    last_name = random.choice(LAST_NAMES[region])

    random_digits = random.randint(10, 999)
    email = f"{first_name.lower()}.{last_name.lower()}{random_digits}@gmail.com"

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        conn.close()
        return generate_unique_user()

    password_hash = generate_password_hash("Test@123")
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        "INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
        (f"{first_name} {last_name}", email, password_hash, created_at)
    )
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return user_id, f"{first_name} {last_name}", email

if __name__ == "__main__":
    user_id, name, email = generate_unique_user()
    print(f"id: {user_id}")
    print(f"name: {name}")
    print(f"email: {email}")