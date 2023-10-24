$(document).ready(function () {
    // Get the query parameters from the current URL
    const urlParams = new URLSearchParams(window.location.search);

    // Check if the 'profileDeleted' query parameter exists and is set to 'true'
    if (urlParams.has('profileDeleted') && urlParams.get('profileDeleted') === 'true') {
        $("#profile-deleted-alert").removeClass("none");

        // fade the notification in
        $("#profile-deleted-alert").fadeTo(1500, 500).slideUp(300, function () {
            $("#profile-deleted-alert").slideUp(300);
        });

        // Remove the 'profileDeleted' query parameter from the URL
        urlParams.delete('profileDeleted');
        const newURL = urlParams.toString() ? `${window.location.pathname}?${urlParams.toString()}` : window.location.pathname;
        history.replaceState({}, document.title, newURL);
    }

    // function to create new profiles
    $('#addProfileForm').on('submit', function (event) {
        event.preventDefault(); // Prevent default behaviour when form is submitted

        // Get the new profile name from the modal form
        var newProfileName = $('#newProfileName').val();
        if (newProfileName.length < 1) {
            alert("Profile Name Must Not Be Empty!");
        }

        // Perform AJAX request to create the new profile
        else {
            // Get CSRF Token from the hidden input field
            var csrftoken = $('input[name=csrfmiddlewaretoken]').val();

            $.ajax({
                url: '/create_profile/',
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken
                },
                data: {
                    'name': newProfileName,
                },
                success: function (data) {
                    // Create a new list item for the profile with the same structure and classes as the existing ones
                    var listItem = $('<li><a class="profile-item" href="#" data-profile-id="' + data.id + '">' + data.name + '</a></li>');

                    // Find the "New Profile" list item and insert the new item before it
                    $('#profile-list li:last').before(listItem);

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

    // Function to handle profile deletion
    $(".delete-profile").click(function (e) {
        var csrftoken = $('input[name=csrfmiddlewaretoken]').val();
        e.preventDefault();

        // Get the profile ID from the data attribute
        var profileId = $(this).data("profile-id");

        // Prompt the user for confirmation
        var confirmDelete = confirm("Are you sure you want to delete this profile?");
        if (confirmDelete) {
            // Send an AJAX request to delete the profile
            $.ajax({
                type: "POST",
                url: "/delete_profile/",
                headers: {
                    'X-CSRFToken': csrftoken
                },
                data: {
                    profile_id: profileId,
                },
                success: function () {
                    // add query parameter to indicated deletion and reload
                    const currentURL = window.location.href;
                    const newURL = `${currentURL}?profileDeleted=true`;
                    window.location.href = newURL;
                }
            });
        }
    });

    // Function to handle "Edit Profile" button click
    $(".edit-profile").click(function (e) {
        e.preventDefault();

        // Get the profile ID from the data attribute
        var profileId = $(this).data("profile-id");

        // Set the profile ID in the form action URL
        var form = $("#editProfileForm");
        form.attr("action", "/edit_profile/" + profileId + "/");

        // Clear the input field
        $("#profileName").val("");

        // Show the modal
        $("#editProfileModal").modal("show");
    });

    // Function to handle form submission
    $("#editProfileForm").submit(function (e) {
        e.preventDefault();
        var csrftoken = $('input[name=csrfmiddlewaretoken]').val();

        // Serialize the form data
        var formData = $(this).serialize();

        // Send an AJAX request to edit the profile
        $.ajax({
            type: "POST",
            url: $(this).attr("action"),
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: formData,
            success: function (data) {
                // Close the modal
                $("#editProfileModal").modal("hide");

                // Reload the profile page
                window.location.href = "/profile/";
            }
        });
    });
});
