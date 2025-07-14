// phoenix/app/static/js/support/new_ticket.js
// Client-side validation for new ticket form

document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.new-ticket-container form');
    if (form) {
        form.addEventListener('submit', function(e) {
            const title = form.title.value.trim();
            const description = form.description.value.trim();
            if (!title || !description) {
                alert('Please fill in all fields.');
                e.preventDefault();
            }
        });
    }
});
