function updateProfileDisplay(profileId) {

    // Fetch the selected profile's name using AJAX
    $.ajax({
        url: '/get_profile_name/' + profileId + '/',
        method: 'GET',
        success: function (data) {
            $('#curr-profile').text(' ' + data.name + ' ');
            $('#display-curr-profile-name').text(' ' + 'Files in Profile: ' + data.name + ' ');

            displayCurrentFiles();

        },
        error: function () {
            alert('Error fetching profile name');
        }
    });

    // Fetch the documents associated with the selected profile using AJAX
    $.ajax({
        url: '/get_documents/' + profileId + '/',
        method: 'GET',
        success: function (data) {
            if (data.length > 0) {
                // Iterate through the documents
                $('#profile-files-list').empty();
                for (var i = 0; i < data.length; i++) {
                    // Create a list item with the document title and a delete button
                    var listItem = $('<li>' + data[i].title + '</li>');

                    // Add delete button to list (for the document)
                    var deleteButton = $('<button>X</button>');
                    deleteButton.data('documentId', data[i].id);
                    deleteButton.addClass('delete-document-button');
                    deleteButton.attr('style', 'background-color: #ff0000; color: #ffffff; width: 18px; height: 18px; line-height: 10px; text-align: center; font-size: 15px; padding: 0;  border: 2px solid #ff0000; float: right; margin-top: 3px;');
                    listItem.append(deleteButton);

                    // Append the document
                    $('#profile-files-list').append(listItem);
                }

            } else {
                // Display 'No Documents' if there are no documents
                $('#profile-files-list').empty().append('<li>No Documents</li>');
            }

        },
        error: function () {
            alert('Error fetching documents');
        }
    });


}

$(document).ready(function () {
    // Attach a click event handler to the profile dropdown items
    $('.profile-item').on('click', function (event) {
        console.log("clicked button")
        event.preventDefault(); // Prevent the default link behavior

        // Get the selected profile ID
        var selectedProfileId = $(this).data('profile-id');
        //uniqueCurrentProfileID = selectedProfileId;
        $('#curr-profile').data('profile-id', selectedProfileId)

        // Update the profile name and documents based on the selected profile ID
        updateProfileDisplay(selectedProfileId);
    });

    // If a currently select profile is included, initialize with those values
    if ($('#curr-profile').data('profile-id') > 0) {
        //uniqueCurrentProfileID = $('#curr-profile-name').data('profile-id')
        updateProfileDisplay($('#curr-profile').data('profile-id'))
    } else {
        // Otherwise initialize the display with 'None' when the page loads
        console.log("current ID is none");
        $('#curr-profile').text(' None ');
        // $('#profile-files-list').empty().append('<li>No Documents</li>');
    }
});


// Add a click event listener for delete buttons
$('#profile-files-list').on('click', '.delete-document-button', function (event) {

    event.preventDefault();
    var csrftoken = $('input[name=csrfmiddlewaretoken]').val();
    console.log(csrftoken);

    var documentId = $(this).data('documentId');
    var listItem = $(this).closest('li'); // Get the parent list item

    const listParent = document.querySelector("#profile-files-list");

    // Send an AJAX request to delete the document by its ID
    $.ajax({
        url: '/delete_document/' + documentId + '/',
        headers: {
            'X-CSRFToken': csrftoken
        },
        method: 'DELETE',
        success: function () {
            // Remove the list item as document was deleted from back-end
            listItem.remove();
            if (listParent.children.length < 1) {
                $('#profile-files-list').append('<li>No Documents</li>');
            }
        },
        error: function () {
            alert('Error deleting document');
        }
    });
});

function displayCurrentFiles() {
    let displayDocs = document.querySelector("#current-docs");
    if (displayDocs)
        displayDocs.classList.remove("none");
}
