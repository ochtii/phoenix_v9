// phoenix/app/static/js/projects/project_settings.js
// Client-side validation for project creation form

document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.project-settings-container form');
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
