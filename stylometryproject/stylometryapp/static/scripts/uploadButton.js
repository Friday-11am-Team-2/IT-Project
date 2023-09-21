// Javascript for making buttons and display work
let fileInput = document.getElementById("upload");
let fileList = document.getElementById("files-list");
let numOfFiles = document.getElementById("num-of-files");

// Define arrays to store file names and file content
const fileNamesArray = [];
const fileContentArray = [];

let nextListItemId = 1; // Initialize a unique identifier for list items

// Javascript for upload button to accept multiple files & uploads
fileInput.addEventListener("change", () => {

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
        deleteButtonCopy.addEventListener("click", (e) => {
            const itemId = e.target.dataset.itemID;

            // Find the index of the item in the array using its unique identifier
            const index = fileNamesArray.findIndex((item) => item.itemId === itemId);

            if (index !== -1) {
                // Remove the corresponding file name and file content from the arrays
                fileNamesArray.splice(index, 1);
                fileContentArray.splice(index, 1);

                // Remove the list item from the DOM
                listItem.remove();

                // Update the number of files selected
                numOfFiles.textContent = `${fileNamesArray.length} Files Selected`;
            }
        });

        deleteButtonCopy.dataset.itemId = nextListItemId;
        nextListItemId++;

        fileContainer.append(deleteButtonCopy);
        listItem.append(fileContainer);
        // console.dir(listItem);
        fileList.appendChild(listItem);

        // Read the file content and add it to the arrays
        reader.onload = (event) => {
            const fileContent = event.target.result;
            fileNamesArray.push({ itemID: deleteButtonCopy.dataset.itemID, name: fileName });


            fileContentArray.push(fileContent);

            // See file name & file content here
            // console.log(`File "${fileName}" content: ${fileContent}`);

            numOfFiles.textContent = `${fileNamesArray.length} Files Selected`;
        };


        // Read the file as text
        reader.readAsText(file);
    }

});
