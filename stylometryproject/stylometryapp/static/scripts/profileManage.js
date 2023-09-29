$(document).ready(function () {
    // Function to handle profile deletion
    $(".delete-profile").click(function (e) {

        var csrftoken = $('input[name=csrfmiddlewaretoken]').val();

        console.log("delete profile clicked");
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
                    // Refresh the page
                    location.reload();
                }
            });
        }
    });
});

$(document).ready(function () {
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
