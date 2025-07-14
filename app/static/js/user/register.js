// phoenix/app/static/js/user/register.js
// Client-side validation for register form

document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.register-container form');
    if (form) {
        form.addEventListener('submit', function(e) {
            const username = form.username.value.trim();
            const email = form.email.value.trim();
            const password = form.password.value;
            if (!username || !email || !password) {
                alert('Please fill in all fields.');
                e.preventDefault();
            }
        });
    }
});
