$(document).ready(function () {
    // check if a profile was deleted earlier
    // Get the query parameters from the current URL
    const urlParams = new URLSearchParams(window.location.search);

    // Check if the 'profileDeleted' query parameter exists and is set to 'true'
    if (urlParams.has('profileDeleted') && urlParams.get('profileDeleted') === 'true') {
        $("#profile-deleted-alert").removeClass("none");
        console.dir($("#profile-deleted-alert"));
        $("#profile-deleted-alert").fadeTo(1500, 500).slideUp(300, function () {
            $("#profile-deleted-alert").slideUp(300);
        });

        // Remove the 'profileDeleted' query parameter from the URL
        urlParams.delete('profileDeleted');
        const newURL = urlParams.toString() ? `${window.location.pathname}?${urlParams.toString()}` : window.location.pathname;
        history.replaceState({}, document.title, newURL);
    }

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
                    // change selected ID to -1 "None"
                    // $('#curr-profile').data('profile-id', -1);
                    // console.log(`changed id to ${$('#curr-profile').data('profile-id')}`)
                    const currentURL = window.location.href;
                    const newURL = `${currentURL}?profileDeleted=true`;
                    window.location.href = newURL;
                    // location.reload();
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
