---
description: create a single dummay user in the database 
allowed-tools: Read, Bash(python3:*)
---

Read Database/db.py to understand the users table schema and the get_db() helper. 

Then write and run a Python script using Bash that: 

1. **Generates realistic names** - First + last name from common names across regions (North, South, East, West)
2. **Creates email**: `{first}.{last}{random_2_3_digit}@gmail.com` (e.g., `rahul.sharma91@gmail.com`)
3. **Password**: Hashes `Test@123` using `werkzeug.security.generate_password_hash()`
4. **created_at**: current_datetime
5. **Duplicate check**: Queries users table for existing email; regenerates if exists until unique.
6. **Insert user**: Uses `get_db()` pattern from `Database.db` module
7. **Output**: Prints id, name, email
8. **Print confirmation**:
    - id
    - name
    - email
