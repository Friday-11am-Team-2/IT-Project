let profileDropdownOptions = document.querySelectorAll(".dropdown-menu li a");
let fileInput = document.getElementById("upload");
let fileList = document.getElementById("files-list");
let numOfFiles = document.getElementById("num-of-files");
const runVerificationButton = document.getElementById("verify-button");

// Define arrays to store file names and file content
const fileNamesArray = [];
const fileContentArray = [];
const FILE_SIZE_LIMIT = 10240;  // in KB

// For the upload in the verify page
fileInput.addEventListener("change", () => {
    // Stops upload if there exists a file that would be too large
    for (const file of fileInput.files) {
        let fileSize = (file.size / 1024).toFixed(2);
        if (fileSize > FILE_SIZE_LIMIT) {
            alert("All uploaded files must be 10MB or less in size!");
            return;
        }
    }

    // update local storage flag to indicate button not clicked
    localStorage.removeItem('buttonClicked');
    runVerificationButton.disabled = false;

    fileList.innerHTML = "";
    if (fileInput.files.length != 0) {
        numOfFiles.textContent = `File Selected`;
    }

    fileNamesArray.length = 0;
    fileContentArray.length = 0;

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
        listItem.innerText = `${fileName}`;

        fileList.appendChild(listItem);

        // Read the file content and add it to the arrays
        reader.onload = (event) => {
            // encode file content (decode in file type handling)
            const uint8Array = new Uint8Array(event.target.result);
            const chunkSize = 65536; // Choose an appropriate chunk size based on your data
            const chunks = [];

            for (let i = 0; i < uint8Array.length; i += chunkSize) {
                const chunk = uint8Array.subarray(i, i + chunkSize);
                const chunkString = String.fromCharCode.apply(null, chunk);
                chunks.push(chunkString);
            }

            const fileContent = btoa(chunks.join(''));

            fileNamesArray.push(fileName);
            fileContentArray.push(fileContent);

            // See file name & file content here
            // console.log(`File "${fileName}" content: ${fileContent}`);
        };

        reader.readAsArrayBuffer(file);
    }


});

// making verify reclickable
let lastElementID = null;
for (let option of profileDropdownOptions) {
    option.addEventListener("click", () => {
        let id = option.getAttribute("data-profile-id");
        if (id != lastElementID) {
            // different option clicked so update
            lastElementID = id;
            // make verify clickable again
            localStorage.removeItem('buttonClicked');
            runVerificationButton.disabled = false;
        }
    })
}

// Add a click event listener for delete buttons
$('#profile-files-list').on('click', '.delete-document-button', function (event) {
    localStorage.removeItem('buttonClicked');
    runVerificationButton.disabled = false;
});