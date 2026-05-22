function displaybuttonformdiv(value) {
    const buttonformdiv = document.querySelectorAll("#button-form-div");
    const buttonfordiv = document.querySelector("#buttonfordiv");
    const buttonforremovediv = document.querySelector("#buttonforremovediv");
    const buttoncheckeditems = document.querySelector("#buttoncheckeditems");

    buttonformdiv.forEach((button) => {
        button.style.display = value;
    });
    if (value == "none") {
        buttonfordiv.style.display = "block";
        buttonforremovediv.style.display = "none";
        buttoncheckeditems.style.display = "none";
    } else {
        buttonfordiv.style.display = "none";
        buttonforremovediv.style.display = "block";
        buttoncheckeditems.style.display = "block";
    }
}

function updatedropdown() {
    const dropdown_menu = document.querySelector(".dropdown-menu");
    const monthyear = JSON.parse(localStorage.getItem("monthyear")) || [];
    const now = new Date();
    const monthNames = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ];
    const monthYear = monthNames[now.getMonth()] + "-" + now.getFullYear();
    if (!monthyear.includes(monthYear)) {
        monthyear.push(monthYear);
        localStorage.setItem("monthyear", JSON.stringify(monthyear));
    }
    monthyear.forEach((item) => {
        const element = document.createElement("li");
        const button = document.createElement("button");
        button.className = "dropdown-item";
        button.role = "button";
        button.name = "monthyear";
        button.value = item.replace("-", "_");
        button.innerText = item;
        element.append(button);
        dropdown_menu.appendChild(element);
    });
}

updatedropdown();

var ROWS_PER_PAGE = 5;
var currentPage = 1;

function getFilteredRows() {
    var dateFrom = document.getElementById('dateFrom').value;
    var dateTo = document.getElementById('dateTo').value;
    var rows = document.querySelectorAll('#table-body tr');
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
        total > 0 ? (start + 1) + '-' + end + ' of ' + total : '0 entries';
    document.getElementById('prevPage').disabled = currentPage <= 1;
    document.getElementById('nextPage').disabled = currentPage >= totalPages;
}

function fetchAndUpdateAnalytics() {
    if (!window.updateAnalyticsFromData) return;
    var dateFrom = document.getElementById('dateFrom').value;
    var dateTo = document.getElementById('dateTo').value;
    var params = new URLSearchParams();
    if (dateFrom) params.set('from', dateFrom);
    if (dateTo) params.set('to', dateTo);
    var qs = params.toString();
    fetch('/api/chart-data' + (qs ? '?' + qs : ''))
        .then(function(r) { return r.json(); })
        .then(function(data) { window.updateAnalyticsFromData(data); });
}

document.addEventListener('DOMContentLoaded', function() {
    if (!document.getElementById('dateFrom')) return;
    updatePagination();
    document.getElementById('dateFrom').addEventListener('change', function() {
        currentPage = 1; updatePagination(); fetchAndUpdateAnalytics();
    });
    document.getElementById('dateTo').addEventListener('change', function() {
        currentPage = 1; updatePagination(); fetchAndUpdateAnalytics();
    });
    document.getElementById('clearDates').addEventListener('click', function() {
        document.getElementById('dateFrom').value = '';
        document.getElementById('dateTo').value = '';
        currentPage = 1; updatePagination(); fetchAndUpdateAnalytics();
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