// phoenix/app/static/js/user/edit_profile.js
// Client-side validation for edit profile form

document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.edit-profile-container form');
    if (form) {
        form.addEventListener('submit', function(e) {
            const about = form.about_me.value.trim();
            const location = form.location.value.trim();
            const website = form.website.value.trim();
            if (website && !/^https?:\/\//.test(website)) {
                alert('Website must start with http:// or https://');
                e.preventDefault();
            }
        });
    }
});
