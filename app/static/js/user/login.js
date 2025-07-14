// phoenix/app/static/js/user/login.js
// Client-side validation for login form

document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.login-container form');
    if (form) {
        form.addEventListener('submit', function(e) {
            const email = form.email.value.trim();
            const password = form.password.value;
            if (!email || !password) {
                alert('Please fill in all fields.');
                e.preventDefault();
            }
        });
    }
});
