function validateProfilePassword(password) {
    var checks = {
        'pw-length': password.length >= 8 && password.length <= 72,
        'pw-letter': /[A-Za-z]/.test(password),
        'pw-number': /[0-9]/.test(password),
        'pw-special': /[!@#$%^&*()_+\-=\[\]{}|;':",.\/<>?\\]/.test(password),
    };
    var allValid = true;
    for (var id in checks) {
        var el = document.getElementById(id);
        if (el) {
            el.style.color = checks[id] ? '#28a745' : '#6c757d';
            el.style.fontWeight = checks[id] ? 'bold' : 'normal';
            if (!checks[id]) allValid = false;
        }
    }
    return allValid;
}

document.addEventListener('DOMContentLoaded', function () {
    var pwInput = document.getElementById('new-password');
    if (pwInput) {
        pwInput.addEventListener('input', function () {
            validateProfilePassword(this.value);
        });
    }

    var pwForm = document.getElementById('change-password-form');
    if (pwForm) {
        pwForm.addEventListener('submit', function (e) {
            e.preventDefault();

            var errDiv = document.getElementById('profile-error');
            var sucDiv = document.getElementById('profile-success');
            errDiv.classList.add('d-none');
            sucDiv.classList.add('d-none');

            var pw = document.getElementById('new-password').value;
            var confirm = document.querySelector('input[name="confirm_password"]').value;

            if (!validateProfilePassword(pw)) {
                errDiv.textContent = 'Password does not meet requirements';
                errDiv.classList.remove('d-none');
                return;
            }
            if (pw !== confirm) {
                errDiv.textContent = 'Passwords do not match';
                errDiv.classList.remove('d-none');
                return;
            }

            var formData = new FormData(pwForm);
            fetch('/profile/change-password', {
                method: 'POST',
                body: formData
            })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (data.ok) {
                    pwForm.reset();
                    document.querySelectorAll('.pw-req').forEach(function (el) {
                        el.style.color = '#6c757d';
                        el.style.fontWeight = 'normal';
                    });
                    sucDiv.textContent = data.message || 'Password updated successfully';
                    sucDiv.classList.remove('d-none');
                } else {
                    errDiv.textContent = data.error || 'An error occurred';
                    errDiv.classList.remove('d-none');
                }
            })
            .catch(function () {
                errDiv.textContent = 'Network error. Please try again.';
                errDiv.classList.remove('d-none');
            });
        });
    }

    var sectionIds = [
        'section-account-info',
        'section-summary',
        'section-recent-transactions',
        'section-category-breakdown',
        'section-spending-by-category',
        'section-category-share',
        'section-change-password'
    ];

    function showSection(id) {
        sectionIds.forEach(function (sid) {
            var el = document.getElementById(sid);
            if (el) {
                el.style.display = sid === id ? '' : 'none';
            }
        });
    }

    function setupDropdown(btnId, menuId) {
        var btn = document.getElementById(btnId);
        var menu = document.getElementById(menuId);
        if (!btn || !menu) return;

        btn.addEventListener('click', function (e) {
            e.stopPropagation();
            var isOpen = menu.classList.contains('open');
            menu.classList.toggle('open');
            btn.classList.toggle('open');
            btn.setAttribute('aria-expanded', !isOpen);
        });

        menu.addEventListener('click', function (e) {
            e.stopPropagation();
        });

        menu.querySelectorAll('.nav-dropdown-item').forEach(function (item) {
            item.addEventListener('click', function () {
                var section = this.dataset.section;
                menu.querySelectorAll('.nav-dropdown-item').forEach(function (i) {
                    i.classList.remove('active');
                });
                this.classList.add('active');
                showSection('section-' + section);
                menu.classList.remove('open');
                btn.classList.remove('open');
                btn.setAttribute('aria-expanded', 'false');
            });
        });
    }

    setupDropdown('dashboard-settings-btn', 'dashboard-settings-menu');
    setupDropdown('privacy-btn', 'privacy-menu');

    var sidebarToggle = document.getElementById('sidebar-toggle');
    var profileGrid = document.querySelector('.profile-grid');
    if (sidebarToggle && profileGrid) {
        sidebarToggle.addEventListener('click', function () {
            var collapsed = profileGrid.classList.toggle('sidebar-collapsed');
            sidebarToggle.innerHTML = collapsed ? '&#9654;' : '&#9664;';
        });
    }

    var accountBtn = document.getElementById('account-settings-btn');
    if (accountBtn) {
        accountBtn.addEventListener('click', function () {
            showSection('section-account-info');
            document.querySelectorAll('.nav-link-item.active').forEach(function (i) {
                i.classList.remove('active');
            });
            this.classList.add('active');
        });
    }

    var editBtn = document.getElementById('account-edit-btn');
    var saveBtn = document.getElementById('account-save-btn');
    var cancelBtn = document.getElementById('account-cancel-btn');
    var displayDiv = document.getElementById('account-info-display');
    var editDiv = document.getElementById('account-info-edit');
    var msgDiv = document.getElementById('account-info-msg');

    function enterEditMode() {
        displayDiv.classList.add('d-none');
        editDiv.classList.remove('d-none');
        msgDiv.classList.add('d-none');
    }

    function exitEditMode() {
        editDiv.classList.add('d-none');
        displayDiv.classList.remove('d-none');
    }

    if (editBtn) {
        editBtn.addEventListener('click', function () {
            document.getElementById('edit-name').value = document.getElementById('display-name').textContent;
            document.getElementById('edit-email').value = document.getElementById('display-email').textContent;
            document.getElementById('edit-phone').value = document.getElementById('display-phone').textContent === 'Not set' ? '' : document.getElementById('display-phone').textContent;
            document.getElementById('edit-address').value = document.getElementById('display-address').textContent === 'Not set' ? '' : document.getElementById('display-address').textContent;
            enterEditMode();
        });
    }

    if (cancelBtn) {
        cancelBtn.addEventListener('click', exitEditMode);
    }

    if (saveBtn) {
        saveBtn.addEventListener('click', function () {
            var formData = new FormData();
            formData.append('name', document.getElementById('edit-name').value);
            formData.append('email', document.getElementById('edit-email').value);
            formData.append('phone', document.getElementById('edit-phone').value);
            formData.append('address', document.getElementById('edit-address').value);

            fetch('/profile/update', {
                method: 'POST',
                body: formData
            })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (data.ok) {
                    document.getElementById('display-name').textContent = document.getElementById('edit-name').value;
                    document.getElementById('display-email').textContent = document.getElementById('edit-email').value;
                    document.getElementById('display-phone').textContent = document.getElementById('edit-phone').value || 'Not set';
                    document.getElementById('display-address').textContent = document.getElementById('edit-address').value || 'Not set';
                    exitEditMode();
                    msgDiv.textContent = data.message;
                    msgDiv.classList.remove('d-none');
                } else {
                    msgDiv.textContent = data.error || 'An error occurred';
                    msgDiv.classList.remove('d-none');
                    msgDiv.className = 'msg-error';
                }
            })
            .catch(function () {
                msgDiv.textContent = 'Network error. Please try again.';
                msgDiv.classList.remove('d-none');
                msgDiv.className = 'msg-error';
            });
        });
    }

    document.addEventListener('click', function () {
        document.querySelectorAll('.nav-dropdown-menu').forEach(function (m) {
            m.classList.remove('open');
        });
        document.querySelectorAll('.nav-dropdown-toggle').forEach(function (b) {
            b.classList.remove('open');
            b.setAttribute('aria-expanded', 'false');
        });
    });

    showSection('section-summary');
});
