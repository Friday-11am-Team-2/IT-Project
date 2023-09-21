// Javascript for submit button (ONLY ON PROFILE)
const submitButton = document.getElementById("submit-button");
if (submitButton) {
    submitButton.addEventListener("click", () => {
        // Get profile ID from docDisplay
        const profileID = uniqueCurrentProfileID;
        if (profileID <= 0) {
            alert("Please select a profile first");
            return;
        }

        const dataToSend = {
            profile_id: profileID, // Add the profile ID to the JSON data
            file_names: fileNamesArray.map(item => item.name), // Extract the 'name' property from each object in fileNamesArray
            file_contents: fileContentArray,
        };

        // checking if there are any files to upload
        if (dataToSend.file_names.length == 0) {
            alert("Please add documents to upload to profile");
            return;
        }


        fetch("/add_profile_docs/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(dataToSend), // Send the modified data
        })
            .then((response) => {
                if (response.ok) {
                    // Reload page if successful
                    location.reload('/profile/');
                }
            })
            .catch((error) => {
                // Handle errors
            });
    });
}