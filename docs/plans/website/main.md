# Website Features Plan — Currency & Edit Expense

---

## 1. Overview

Add two features to the Flask expense tracker:

1. **Multi-currency support** — users select their country; amounts display with the correct currency symbol and formatting
2. **Edit expense inline** — click an expense row to edit it via modal; delete expense from modal

Both rely on a per-user `currency_code` field stored in the `users` table.

---

## 2. Currency Support

### 2.1 Supported Currencies

| Country | Currency | Symbol | Code |
|---|---|---|---|
| India | Indian Rupee | ₹ | INR |
| United Kingdom | British Pound | £ | GBP |
| United States | US Dollar | $ | USD |
| European Union | Euro | € | EUR |
| Japan | Japanese Yen | ¥ | JPY |

### 2.2 Database Changes

**Add to `users` table:**
```sql
ALTER TABLE users ADD COLUMN currency_code TEXT DEFAULT 'USD';
```

Update `test.py` startup — run once (safe for existing users).

**New column:** `currency_code` — stores 3-letter ISO code.

### 2.3 Config

Create `Schemas/currency.py`:
```python
CURRENCIES = [
    {"name": "India", "code": "INR", "symbol": "₹"},
    {"name": "United Kingdom", "code": "GBP", "symbol": "£"},
    {"name": "United States", "code": "USD", "symbol": "$"},
    {"name": "European Union", "code": "EUR", "symbol": "€"},
    {"name": "Japan", "code": "JPY", "symbol": "¥"},
]

def get_currency_by_code(code: str) -> dict | None:
    for c in CURRENCIES:
        if c["code"] == code:
            return c
    return None
```

### 2.4 New Routes

| Route | Method | Description |
|---|---|---|
| `/settings` | GET | Render settings page with currency dropdown |
| `/settings/currency` | POST | Update user's currency preference |

### 2.5 Frontend Changes

**Settings page** (`templates/settings.html`):
- Dropdown to select country/currency
- Show current selection
- Save button → POST to `/settings/currency`

**Dashboard header** (`templates/index.html`):
- Add currency selector or link to settings
- Display current symbol in total and table

**Expense table** (`templates/index.html`):
- Replace hardcoded `₹` with `{{ currency_symbol }}` from context
- Format amounts with 2 decimal places (INR/JPY no decimals)

**Add expense form** (`templates/index.html`):
- Replace hardcoded `₹` prefix with `{{ currency_symbol }}`

### 2.6 Backend Changes

**`test.py` — `get_user_currency()` helper:**
```python
def get_user_currency(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT currency_code FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    code = (row["currency_code"] if row else "USD") or "USD"
    from Schemas.currency import get_currency_by_code
    return get_currency_by_code(code)
```

**Dashboard route** — pass `currency_symbol` and `currency_code` to template.

**Register route** — set default `currency_code` to "USD".

---

## 3. Edit Expense (Inline Modal)

### 3.1 Route

| Route | Method | Description |
|---|---|---|
| `/edit-expense` | POST | Update expense by id (amount, category, date, description) |

### 3.2 Modal HTML (`templates/index.html`)

```html
<!-- Edit Expense Modal -->
<div class="modal" id="editModal">
  <form id="editExpenseForm" method="POST" action="/edit-expense">
    <input type="hidden" name="expense_id" id="edit_expense_id">
    <!-- Category dropdown -->
    <select name="category" id="edit_category">
      <!-- options from CATEGORIES -->
    </select>
    <!-- Amount input -->
    <input type="number" name="amount" id="edit_amount" step="0.01" required>
    <!-- Date input -->
    <input type="date" name="date" id="edit_date" required>
    <!-- Description -->
    <textarea name="description" id="edit_description" maxlength="500"></textarea>
    <!-- Delete button -->
    <button type="button" onclick="deleteExpense()">Delete</button>
    <!-- Save + Cancel -->
  </form>
</div>
```

### 3.3 JavaScript (`static/main.js`)

```javascript
function openEditModal(row) {
  document.getElementById('edit_expense_id').value = row.id;
  document.getElementById('edit_category').value = row.category;
  document.getElementById('edit_amount').value = row.amount;
  document.getElementById('edit_date').value = row.date;
  document.getElementById('edit_description').value = row.description || '';
  showModal();
}

function deleteExpense() {
  // Submit hidden delete form to /delete-expense
}

function showModal() { /* toggle display */ }
```

### 3.4 Routes (`test.py`)

**`/edit-expense` (POST):**
```python
@app.route("/edit-expense", methods=["POST"])
def edit_expense():
    # Validate user owns expense
    # Update amount, category, date, description
    # Redirect to dashboard
```

**`/delete-expense` (POST):**
```python
@app.route("/delete-expense", methods=["POST"])
def delete_expense():
    # Validate user owns expense (by expense_id)
    # DELETE FROM expenses WHERE id = ? AND user_id = ?
    # Redirect to dashboard
```

### 3.5 Validation

- Amount > 0, max 2 decimal places
- Category in CATEGORIES
- Date in YYYY-MM-DD format
- Description max 500 chars
- User must own the expense

---

## 4. Edit/Delete by ID (Replace ID-less Logic)

### 4.1 Current Problem

The current `/remove` route uses `category + amount + date` to match — this is fragile and can delete the wrong expense.

### 4.2 Solution

All expense operations now use `expense_id` as the primary key.

**Database:** No schema change needed (id already exists).

**Templates:** Pass `expense.id` in hidden fields and form actions.

### 4.3 New Route — `/delete-expense` (POST)

```python
@app.route("/delete-expense", methods=["POST"])
def delete_expense():
    user = get_current_user(...)
    expense_id = request.form.get("expense_id", type=int)
    user_id = user["id"]

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM expenses WHERE id = ? AND user_id = ?",
        (expense_id, user_id)
    )
    conn.commit()
    conn.close()
    return redirect("/dashboard")
```

### 4.4 Remove Checkbox Form

Replace multi-checkbox form with one per row:
```html
<form method="POST" action="/delete-expense" class="delete-form">
  <input type="hidden" name="expense_id" value="{{ row[5] }}">
  <button type="submit" class="delete-btn">X</button>
</form>
```

---

## 5. Files to Change

| File | Action |
|---|---|
| `Database/db.py` | Add `ALTER TABLE` migration for `currency_code` |
| `Schemas/currency.py` | Create — currency list and lookup |
| `test.py` | Add currency/settings routes, edit/delete routes, dashboard currency context |
| `templates/index.html` | Replace hardcoded `₹`, add edit modal, update row buttons |
| `templates/settings.html` | Create — currency selection page |
| `static/main.js` | Add `openEditModal`, `deleteExpense`, `showModal` |
| `static/style.css` | Modal styles |

---

## 6. Execution Order

1. **Create `Schemas/currency.py`** — currency data and lookup
2. **Update `Database/db.py`** — add `ALTER TABLE` migration
3. **Update `test.py`** — `get_user_currency()` helper, dashboard passes currency context
4. **Update `templates/index.html`** — replace hardcoded `₹`, add edit modal, remove checkbox form
5. **Create `templates/settings.html`** — currency selection page
6. **Add routes to `test.py`** — `/settings`, `/settings/currency`, `/edit-expense`, `/delete-expense`
7. **Update `static/main.js`** — modal open/close/edit/delete
8. **Update `static/style.css`** — modal styling

---

## 7. Considerations

- **Default currency** — new users get USD; existing users with NULL get USD
- **Existing expenses** — amounts stored as numbers in DB, currency symbol is display-only
- **Format** — JPY/INR displayed without decimals, others with 2 decimals
- **Security** — all expense operations verify `user_id` matches session user
- **Delete UX** — confirm before delete? Or instant with undo toast?