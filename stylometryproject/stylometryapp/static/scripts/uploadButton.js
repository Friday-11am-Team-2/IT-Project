// Javascript for making buttons and display work
let fileInput = document.getElementById("upload");
let fileList = document.getElementById("files-list");
let numOfFiles = document.getElementById("num-of-files");

// Define arrays to store file names and file content
const fileNamesArray = [];
const fileContentArray = [];

// Javascript for upload button 
fileInput.addEventListener("change", () => {
    // Clear previous selections
    fileList.innerHTML = "";
    numOfFiles.textContent = `${fileInput.files.length} Files Selected`;

    // Reset arrays for each new selection
    fileNamesArray.length = [];
    fileContentArray.length = [];

    // For each file selected, create a list item and add it to the list
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

            // TO DO - ADD TREATMENT FOR FILE TYPES (either restrict to .txt/add more)
            fileContentArray.push(fileContent);

            // You can perform further processing with the file content here
            console.log(`File "${fileName}" content: ${fileContent}`);
        };

        // Read the file as text
        reader.readAsText(file);
    }
});