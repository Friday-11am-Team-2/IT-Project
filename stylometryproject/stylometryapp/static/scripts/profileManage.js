$(document).ready(function () {
    // Function to handle profile deletion
    $(".delete-profile").click(function (e) {
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
                url: "/delete_profile/",  // Create a Django view for this URL
                data: {
                    profile_id: profileId,
                    csrfmiddlewaretoken: '{{ csrf_token }}'  // Include the CSRF token
                },
                success: function () {
                    // Refresh the page or update the UI as needed
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

        // Serialize the form data
        var formData = $(this).serialize();

        // Send an AJAX request to edit the profile
        $.ajax({
            type: "POST",
            url: $(this).attr("action"),
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
