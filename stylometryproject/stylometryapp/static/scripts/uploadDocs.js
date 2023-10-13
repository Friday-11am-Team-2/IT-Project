// Javascript for making buttons and display work
let fileInput = document.getElementById("upload");
let fileList = document.getElementById("files-list");
let numOfFiles = document.getElementById("num-of-files");

// Define arrays to store file names and file content
const fileNamesArray = [];
const fileContentArray = [];

let nextListItemId = 1; // Initialize a unique identifier for list items
const FILE_SIZE_LIMIT = 10240;  // in KB

// Javascript for upload button to accept multiple files & uploads
fileInput.addEventListener("change", () => {

    // Stops upload if there exists a file that would be too large
    for (const file of fileInput.files) {
        let fileSize = (file.size / 1024).toFixed(2);
        if (fileSize > FILE_SIZE_LIMIT) {
            alert("All uploaded files must be 10MB or less in size!");
            return;
        }
    }

    // For each file selected, create a list item and add it to the list
    for (const file of fileInput.files) {
        let reader = new FileReader();
        let listItem = document.createElement("li");
        let fileName = file.name;
        let fileSize = (file.size / 1024).toFixed(1);

        if (fileSize >= 1024) {
            fileSize = (fileSize / 1024).toFixed(1);
        }

        // div to contain list content and button
        let fileContainer = document.createElement("div");
        fileContainer.classList.add("d-flex", "justify-content-between");

        let span = document.createElement("span");
        span.innerText = `${fileName}`;

        fileContainer.append(span);


        // add button to listItem to delete
        let deleteButtonCopy = document.querySelector(".edit.delete-profile").cloneNode(true);

        deleteButtonCopy["itemID"] = nextListItemId++;
        console.dir(deleteButtonCopy);

        deleteButtonCopy.addEventListener("click", (e) => {
            const itemID = deleteButtonCopy.itemID;

            // Find the index of the item in the array using its unique identifier
            const index = fileNamesArray.findIndex((item) => item.itemID === itemID);

            if (index !== -1) {
                // Remove the corresponding file name and file content from the arrays
                fileNamesArray.splice(index, 1);
                fileContentArray.splice(index, 1);

                // Remove the list item from the DOM
                listItem.remove();

                // Update the number of files selected
                if (fileNamesArray.length == 1)
                    numOfFiles.textContent = `${fileNamesArray.length} File Selected`;
                else
                    numOfFiles.textContent = `${fileNamesArray.length} Files Selected`;
            }
        });

        fileContainer.append(deleteButtonCopy);
        listItem.append(fileContainer);
        fileList.appendChild(listItem);

        // Read the file content and add it to the arrays
        reader.onload = (event) => {
            // encode file content (decode in file type handling)
            const fileContent = btoa(String.fromCharCode(...new Uint8Array(event.target.result)));

            fileNamesArray.push({ itemID: deleteButtonCopy.itemID, name: fileName });


            fileContentArray.push(fileContent);

            // See file name & file content here
            // console.log(`File "${fileName}" content: ${fileContent}`);

            if (fileNamesArray.length == 1)
                numOfFiles.textContent = `${fileNamesArray.length} File Selected`;
            else
                numOfFiles.textContent = `${fileNamesArray.length} Files Selected`;
        };


        // Read file as byte string
        //reader.readAsText(file);
        reader.readAsArrayBuffer(file);

    }

});


// Javascript for submit button (ONLY ON PROFILE)
const submitButton = document.getElementById("submit-button");
if (submitButton) {
    submitButton.addEventListener("click", () => {

        csrftoken = document.getElementsByName("csrfmiddlewaretoken")[0].value;
        console.log(csrftoken);

        // Get profile ID from docDisplay
        const profileID = $('#curr-profile').data('profile-id');

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
                "X-CSRFToken": csrftoken,
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
