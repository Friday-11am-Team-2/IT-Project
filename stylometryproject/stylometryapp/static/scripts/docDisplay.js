let uniqueCurrentProfileID = 0;

// Function to update the profile name and documents
function updateProfileDisplay(profileId) {

    // Fetch the selected profile's name using AJAX
    $.ajax({
        url: '/get_profile_name/' + profileId + '/',
        method: 'GET',
        success: function(data) {
            $('#curr-profile-name').text(' ' + data.name + ' ');
            $('#display-curr-profile-name').text(' ' + data.name + ' ');
        },
        error: function() {
            alert('Error fetching profile name');
        }
    });

    // Fetch the documents associated with the selected profile using AJAX
    $.ajax({
        url: '/get_documents/' + profileId + '/',
        method: 'GET',
        success: function(data) {
            if (data.length > 0) {
                $('#profile-files-list').empty();
                for (var i = 0; i < data.length; i++) {
                    $('#profile-files-list').append('<li>' + data[i].title + '</li>');
                }
            } else {
                // Display 'No Documents' if there are no documents
                $('#profile-files-list').empty().append('<li>No Documents</li>');
            }
        },
        error: function() {
            alert('Error fetching documents');
        }
    });
}

$(document).ready(function() {
    // Attach a click event handler to the profile dropdown items
    $('.profile-item').on('click', function(event) {
        event.preventDefault(); // Prevent the default link behavior
        
        // Get the selected profile ID
        var selectedProfileId = $(this).data('profile-id');
        uniqueCurrentProfileID = selectedProfileId;

        // Update the profile name and documents based on the selected profile ID
        updateProfileDisplay(selectedProfileId);
    });

    // Initialize the display with 'None' when the page loads
    $('#curr-profile-name').text(' None ');
    $('#profile-files-list').empty().append('<li>No Documents</li>');
});

