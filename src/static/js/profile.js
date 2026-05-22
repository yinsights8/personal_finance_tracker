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
