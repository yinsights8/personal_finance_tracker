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
            var pw = document.getElementById('new-password').value;
            var confirm = document.querySelector('input[name="confirm_password"]').value;
            var errDiv = document.getElementById('profile-error');

            if (!validateProfilePassword(pw)) {
                e.preventDefault();
                if (errDiv) {
                    errDiv.style.display = 'block';
                    errDiv.textContent = 'Password does not meet requirements';
                }
                return;
            }
            if (pw !== confirm) {
                e.preventDefault();
                if (errDiv) {
                    errDiv.style.display = 'block';
                    errDiv.textContent = 'Passwords do not match';
                }
            }
        });
    }
});
