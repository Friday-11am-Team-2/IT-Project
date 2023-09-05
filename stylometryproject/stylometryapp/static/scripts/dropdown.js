// $(document).ready(function() {
//     // Attach a click event handler to each dropdown item
//     $('.dropdown-item').on('click', function(e) {
//         e.preventDefault();
        
//         // Get the selected profile's name and ID
//         var profileName = $(this).text();
//         profileId = $(this).data('profile-id');
        
//         // Set the dropdown button text to the selected profile's name
//         $('#curr-profile-name').text(profileName);
        
//         // You can also store the selected profile's ID in a hidden input field
//         $('#selected-profile-id').val(profileId);
//     });
// });

$(document).ready(function() {
    // Attach a click event handler to the "Add Profile" button
    $('#addProfileBtn').on('click', function() {
        // Get the new profile name from the modal form
        var newProfileName = $('#newProfileName').val();
        
        // Perform AJAX request to create the new profile
        $.ajax({
            url: '/create_profile/',  // Update with your Django URL for creating profiles
            method: 'POST',
            data: {
                'name': newProfileName,
                // Include any additional data you need to send to the server
            },
            success: function(data) {
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
            error: function() {
                alert('Error adding profile');
            }
        });
    });
});
