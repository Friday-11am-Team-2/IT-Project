// Javascript for making buttons and display work
let fileInput = document.getElementById("upload");
let fileList = document.getElementById("files-list");
let numOfFiles = document.getElementById("num-of-files");

// Define arrays to store file names and file content
const fileNamesArray = [];
const fileContentArray = [];

fileInput.addEventListener("change", () => {
    // Clear previous selections
    fileList.innerHTML = "";
    numOfFiles.textContent = `${fileInput.files.length} Files Selected`;

    // Reset arrays for each new selection
    fileNamesArray.length = 0;
    fileContentArray.length = 0;

    for (const file of fileInput.files) {
        let reader = new FileReader();
        let listItem = document.createElement("li");
        let fileName = file.name;
        let fileSize = (file.size / 1024).toFixed(1);

        listItem.innerHTML = `<p>${fileName}</p>`;

        if (fileSize >= 1024) {
            fileSize = (fileSize / 1024).toFixed(1);
        }

        fileList.appendChild(listItem);

        // Read the file content and add it to the arrays
        reader.onload = (event) => {
            const fileContent = event.target.result;
            fileNamesArray.push(fileName);
            fileContentArray.push(fileContent);

            // You can perform further processing with the file content here
            console.log(`File "${fileName}" content: ${fileContent}`);
        };

        // Read the file as text
        reader.readAsText(file);
    }
});

const submitButton = document.getElementById("submit-button");
submitButton.addEventListener("click", () => {
    // Send the file data to Django here
    // You can use an AJAX request or other methods to send this data
    // Example using fetch:

    // Get profile ID from docDisplay
    const profileID = uniqueCurrentProfileID;
    if (profileID <= 0) {
        alert("Please select a profile first");
        return;
    }

    const dataToSend = {
        profile_id: profileID, // Add the profile ID to the JSON data
        file_names: fileNamesArray,
        file_contents: fileContentArray,
    };

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