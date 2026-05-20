# Database Spec-Development

---

# 1. Overview

This database is the core foundation layer of the Expense Tracker application.

The database implementation will use SQLite.

All future features depend on this database being implemented correctly, including:

- Authentication
- User profiles
- Expense tracking
- Analytics
- Budgeting

This phase is responsible for building a stable and reusable persistence layer before API or frontend development begins.

---

# 2. Depends On

Nothing.

This is the starting phase of the project.

---

# 3. Testing

Create a small Python file named:

```text
test.py
```

This file must:

- Initialize the database
- Seed demo data
- Validate foreign key enforcement
- Validate duplicate protection
- Print success messages
- Raise clear errors if implementation fails

---

# 4. Database Schema

## A. Users Table

| Column | Type | Constraints |
|---|---|---|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT |
| name | TEXT | NOT NULL |
| email | TEXT | UNIQUE, NOT NULL |
| password_hash | TEXT | NOT NULL |
| created_at | TEXT | DEFAULT datetime('now') |

---

## B. Expenses Table

| Column | Type | Constraints |
|---|---|---|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT |
| user_id | INTEGER | FOREIGN KEY → users(id), NOT NULL |
| amount | REAL | NOT NULL |
| category | TEXT | NOT NULL |
| date | TEXT | NOT NULL (YYYY-MM-DD format) |
| description | TEXT | NULLABLE |
| created_at | TEXT | DEFAULT datetime('now') |

---

# 5. Functions To Implement (`Database/db.py`)

## A. `get_db()`

Responsibilities:

- Open SQLite connection
- Return active connection
- Enable:
  - foreign key enforcement
  - dictionary-like row access

Requirements:

```python
conn.row_factory = sqlite3.Row
conn.execute("PRAGMA foreign_keys = ON")
```

---

## B. `init_db()`

Responsibilities:

- Create database tables
- Use:

```sql
CREATE TABLE IF NOT EXISTS
```

Requirements:

- Safe to call multiple times
- Must not recreate existing tables
- Must ensure schema exists before application usage

Tables to create:

- users
- expenses

---

## C. `seed_db()`

Responsibilities:

### Step 1 — Check Existing Data

Check whether users table already contains data.

Behavior:

- If data exists:
  - Return early
  - Prevent duplicate inserts

---

### Step 2 — Insert Demo User

Insert exactly one demo user:

| Field | Value |
|---|---|
| name | Demo User |
| email | demo@spendly.com |
| password | demo123 |

Password must be hashed using:

```python
from werkzeug.security import generate_password_hash
```

---

### Step 3 — Insert Sample Expenses

Insert exactly 8 expenses.

Requirements:

- All linked to demo user
- Cover multiple categories
- Dates spread across current month
- At least one expense per category

---

# 6. Configurations

Do NOT hardcode configuration values unless used as fallback values.

Create:

```text
Database/config.py
```

Responsibilities:

- Load environment variables
- Store application settings
- Store database path
- Store configurable defaults

Suggested approach:

- os.getenv()
- python-dotenv (optional)

Example:

```python
DATABASE_NAME = os.getenv("DATABASE_NAME", "expense_tracker.db")
```

---

# 7. Schemas

Schemas control:

- API input validation
- API output validation
- Database request structure

Use:

- Pydantic

Create the following schema files:

```text
Schemas/user.py
Schemas/expense.py
Schemas/category.py
```

---

## Example Schema

```python
from pydantic import BaseModel

class ExpenseCreate(BaseModel):
    title: str
    amount: float
    category_id: int
```

---

# 8. Files To Create

## Database Layer

```text
Database/db.py
Database/config.py
```

---

## Schema Layer

```text
Schemas/user.py
Schemas/expense.py
Schemas/category.py
```

---

## Testing

```text
test.py
```

---

# 9. Dependencies

Use:

- uv package manager
- sqlite3
- werkzeug.security
- pydantic

Install dependencies using:

```bash
uv add pydantic werkzeug python-dotenv
```

---

# 10. Categories (Fixed Values)

Use exactly these category values:

1. Food
2. Transport
3. Bills
4. Health
5. Entertainment
6. Shopping
7. Other

These values must remain consistent across:

- database
- API
- frontend
- validation

---

# 11. Rules For Implementation

## Database Rules

- No ORMs
- No SQLAlchemy
- Use raw SQLite only
- Use parameterized queries only
- Never use string formatting in SQL
- use python version >= 3.10
- create virtual env. 
  
Correct:

```python
cursor.execute(
    "SELECT * FROM users WHERE email = ?",
    (email,)
)
```

Incorrect:

```python
cursor.execute(
    f"SELECT * FROM users WHERE email = '{email}'"
)
```

---

## Connection Rules

Enable on every connection:

```sql
PRAGMA foreign_keys = ON
```

---

## Data Rules

- Store amount as REAL
- Never store money as INTEGER
- Dates must use:
  - YYYY-MM-DD

---

## Password Rules

Hash passwords using:

```python
from werkzeug.security import generate_password_hash
```

Never store plain text passwords.

---

## Seed Rules

`seed_db()` must:

- Prevent duplicate inserts
- Be idempotent
- Safely run multiple times

---

## Schema Rules

Use Pydantic for:

- request validation
- response validation
- type safety

---

# 12. Expected Behavior

## `get_db()`

Must return:

- Working SQLite connection
- Dictionary-like row access
- Foreign key enforcement enabled

---

## `init_db()`

Must:

- Create tables safely
- Work on repeated runs
- Not destroy existing data

---

## `seed_db()`

Must:

- Insert demo data once
- Prevent duplicates
- Repeated calls must not create duplicate records

---

## Database Constraints

Database must enforce:

### Unique Emails

Duplicate emails must fail.

---

### Foreign Key Relationships

Invalid `user_id` values must fail.

---

# 13. Error Handling Expectations

## Duplicate Email

Expected:

```text
UNIQUE constraint failed
```

---

## Invalid Foreign Key

Expected:

```text
FOREIGN KEY constraint failed
```

---

## Invalid Queries

Behavior:

- Raise clear exceptions
- Help debugging
- Avoid silent failures

---

# 14. Definition Of Done

Project is complete when:

- Database file is created automatically
- Both tables exist correctly
- Schema matches specification
- Demo user exists
- Password is hashed
- 8 sample expenses exist
- Categories are correctly distributed
- No duplicate seed data exists
- `test.py` runs successfully
- Foreign key enforcement works
- All SQL queries are parameterized
- No ORM is used
- Configurations use environment variables/settings only

---

# 15. Suggested Project Structure

```text
project-root/
│
├── Database/
│   ├── db.py
│   └── config.py
│
├── Schemas/
│   ├── user.py
│   ├── expense.py
│   └── category.py
│
├── test.py
├── .env
├── pyproject.toml
└── README.md
```

---

# 16. Suggested Environment Variables

Example `.env`

```env
DATABASE_NAME=expense_tracker.db
DEBUG=True
```

---

# 17. Recommended SQLite Connection Example

```python
import sqlite3

conn = sqlite3.connect("expense_tracker.db")
conn.row_factory = sqlite3.Row
conn.execute("PRAGMA foreign_keys = ON")
```

---

# 18. Notes

This implementation is intentionally simple and foundational.

The goal is:

- correctness
- stability
- clean architecture
- safe database handling

Advanced engineering patterns are intentionally excluded at this stage.