# Dashboard Table: Pagination + Date Range Filter

## Overview

Modify the dashboard expense table to show only 5 rows per page with pagination controls, and add a date range filter to scope the data.

## Files to Modify

| File | Change |
|------|--------|
| `templates/index.html` | Add date inputs, `data-date` attr on rows, pagination controls |
| `static/main.js` | Add client-side pagination + date filtering logic |

## Architecture

**Client-side (JavaScript).** No Python/SQL changes. The `data` list already contains all rows rendered into the table. JS handles filtering and pagination.

## `templates/index.html` — 3 Edits

### 1. Date range inputs (between `{% if data %}` and `<form>`)

```html
{% if data %}
<div class="d-flex align-items-center gap-2 mb-2 flex-wrap">
    <label class="text-light small fw-semibold">Select dates</label>
    <input type="date" id="dateFrom" class="form-control form-control-sm" style="width:auto; max-width:160px;">
    <span class="text-muted small">to</span>
    <input type="date" id="dateTo" class="form-control form-control-sm" style="width:auto; max-width:160px;">
    <button class="btn btn-sm btn-outline-secondary" id="clearDates">Clear</button>
</div>
```

### 2. Add `data-date` to each `<tr>`

```html
<tr data-date="{{row[2]}}">
```

### 3. Pagination controls (after Cancel button, before `{% endif %}`)

```html
<div class="d-flex justify-content-end align-items-center gap-2 mt-2">
    <span class="text-muted small" id="paginationInfo"></span>
    <button class="btn btn-sm btn-outline-light" id="prevPage" disabled>&lt;&lt; Previous</button>
    <button class="btn btn-sm btn-outline-light" id="nextPage">Next &gt;&gt;</button>
</div>
```

## `static/main.js` — Add functions (preserve existing)

Add after existing code:

```javascript
const ROWS_PER_PAGE = 5;
let currentPage = 1;

function getFilteredRows() {
    const dateFrom = document.getElementById('dateFrom').value;
    const dateTo = document.getElementById('dateTo').value;
    const rows = document.querySelectorAll('#table-body tr');
    return Array.from(rows).filter(function(row) {
        var d = row.dataset.date;
        if (dateFrom && d < dateFrom) return false;
        if (dateTo && d > dateTo) return false;
        return true;
    });
}

function updatePagination() {
    var filtered = getFilteredRows();
    var total = filtered.length;
    var totalPages = Math.ceil(total / ROWS_PER_PAGE) || 1;

    if (currentPage > totalPages) currentPage = totalPages;
    if (currentPage < 1) currentPage = 1;

    document.querySelectorAll('#table-body tr').forEach(function(r) { r.style.display = 'none'; });
    var start = (currentPage - 1) * ROWS_PER_PAGE;
    var end = Math.min(start + ROWS_PER_PAGE, total);
    for (var i = start; i < end; i++) {
        if (filtered[i]) filtered[i].style.display = '';
    }

    document.getElementById('paginationInfo').textContent =
        total > 0 ? start + 1 + '-' + end + ' of ' + total : '0 entries';
    document.getElementById('prevPage').disabled = currentPage <= 1;
    document.getElementById('nextPage').disabled = currentPage >= totalPages;
}

document.addEventListener('DOMContentLoaded', function() {
    if (!document.getElementById('dateFrom')) return;
    updatePagination();
    document.getElementById('dateFrom').addEventListener('change', function() {
        currentPage = 1; updatePagination();
    });
    document.getElementById('dateTo').addEventListener('change', function() {
        currentPage = 1; updatePagination();
    });
    document.getElementById('clearDates').addEventListener('click', function() {
        document.getElementById('dateFrom').value = '';
        document.getElementById('dateTo').value = '';
        currentPage = 1; updatePagination();
    });
    document.getElementById('prevPage').addEventListener('click', function() {
        if (currentPage > 1) { currentPage--; updatePagination(); }
    });
    document.getElementById('nextPage').addEventListener('click', function() {
        var filtered = getFilteredRows();
        var totalPages = Math.ceil(filtered.length / ROWS_PER_PAGE) || 1;
        if (currentPage < totalPages) { currentPage++; updatePagination(); }
    });
});
```

## Behaviour

| Action | Result |
|--------|--------|
| Page load | Top 5 rows visible, Previous disabled |
| Click Next | Shows rows 6–10, Previous enabled |
| Click Previous | Shows rows 1–5, Previous disabled |
| Pick date From | Page 1, filter rows >= date |
| Pick date To | Page 1, filter rows <= date |
| Clear dates | Page 1, all rows |
| Remove checked items | Works as before (hidden checkboxes still submit) |
