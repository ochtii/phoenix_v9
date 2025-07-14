// phoenix/app/static/js/base.js
// Base JS for Phoenix web application

document.addEventListener('DOMContentLoaded', function() {
    // Example: Show flash messages if present
    const flashes = document.querySelectorAll('.flash-message');
    flashes.forEach(flash => {
        setTimeout(() => {
            flash.style.display = 'none';
        }, 4000);
    });
});
