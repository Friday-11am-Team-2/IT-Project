$(document).ready(function () {
    // Attach a click event handler to the "Add Profile" button
    $('#addProfileBtn').on('click', function () {
        // Get the new profile name from the modal form
        var newProfileName = $('#newProfileName').val();
        if (newProfileName.length < 1) {
            alert("Profile Name Must Not Be Empty!");
        }
        // Perform AJAX request to create the new profile
        else {
            console.log("Creating new profile");

            // Get CSRF Token from the hidden input field
            var csrftoken = $('input[name=csrfmiddlewaretoken]').val();

            $.ajax({
                url: '/create_profile/',  // Update with your Django URL for creating profiles
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken
                },
                data: {
                    'name': newProfileName,
                    // TO DO? - any new profiles fields in the future go here
                },
                success: function (data) {
                    // Create a new list item for the profile with the same structure and classes as the existing ones
                    var listItem = $('<li><a class="profile-item" href="#" data-profile-id="' + data.id + '">' + data.name + '</a></li>');

                    // Find the "New Profile" list item and insert the new item before it
                    $('#profile-list li:last').before(listItem);;

                    // Clear the modal form and close the modal
                    $('#newProfileName').val('');
                    $('#addProfileModal').modal('hide');

                    // Reload page
                    location.reload();
                },
                error: function () {
                    alert('Error adding profile');
                }
            });
        }

    });
});
