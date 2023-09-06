let uniqueCurrentProfileID = 0;
let uniqueCurrentProfileName = "";

// Function to update the profile name and documents
function updateProfileDisplay(profileId) {

    // Fetch the selected profile's name using AJAX
    $.ajax({
        url: '/get_profile_name/' + profileId + '/',
        method: 'GET',
        success: function(data) {
            $('#curr-profile-name').text(' ' + data.name + ' ');
            $('#display-curr-profile-name').text(' ' + data.name + ' ');
            uniqueCurrentProfileName = data.name;
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
                    // Create a list item with the document title and a delete button
                    var listItem = $('<li>' + data[i].title + '</li>');
                    var deleteButton = $('<button>X</button>');
                    deleteButton.data('documentId', data[i].id); // Store document ID as data
                    deleteButton.addClass('delete-document-button');
                    deleteButton.attr('style', 'background-color: #ff0000; color: #ffffff; width: 20px; height: 20px; line-height: 10px; text-align: center; font-size: 15px; padding: 0;  border: 2px solid #ff0000; float: right');


                    listItem.append(deleteButton);
                    $('#profile-files-list').append(listItem);
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


// Add a click event listener for delete buttons
$('#profile-files-list').on('click', '.delete-document-button', function(event) {
    event.preventDefault();
    var documentId = $(this).data('documentId');
    var listItem = $(this).closest('li'); // Get the parent list item

    // Send an AJAX request to delete the document by its ID
    $.ajax({
        url: '/delete_document/' + documentId + '/', // Replace with your Django endpoint
        method: 'DELETE',
        success: function() {
            // Document deleted successfully, you can update the UI as needed
            listItem.remove();
        },
        error: function() {
            alert('Error deleting document');
        }
    });
});