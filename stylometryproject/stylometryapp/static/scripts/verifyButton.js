// Javascript for making buttons and display work
let profileDropdownOptions = document.querySelectorAll(".dropdown-menu li a");
let fileInput = document.getElementById("upload");
let fileList = document.getElementById("files-list");
let numOfFiles = document.getElementById("num-of-files");
const runVerificationButton = document.getElementById("verify-button");

// Define arrays to store file names and file content
const fileNamesArray = [];
const fileContentArray = [];

// For the upload in the verify page
fileInput.addEventListener("change", () => {
    // make verify clickable again
    
    localStorage.removeItem('buttonClicked');
    runVerificationButton.disabled = false;


    fileList.innerHTML = "";
    if (fileInput.files.length != 0) {
        numOfFiles.textContent = `File Selected`;
    }

    fileNamesArray.length = 0;
    fileContentArray.length = 0;

    // For each file selected, create a list item and add it to the list
    for (const file of fileInput.files) {
        let reader = new FileReader();
        let listItem = document.createElement("li");
        let fileName = file.name;
        // let fileSize = (file.size / 1024).toFixed(1);

        listItem.innerText = `${fileName}`;

        //if (fileSize >= 1024) {
        //    fileSize = (fileSize / 1024).toFixed(1);
        //}

        fileList.appendChild(listItem);

        // Read the file content and add it to the arrays
        reader.onload = (event) => {
            const fileContent = event.target.result;
            fileNamesArray.push(fileName);


            // TO DO - ADD TREATMENT FOR FILE TYPES (either restrict to .txt/add more)
            fileContentArray.push(fileContent);

            // See file name & file content here
            console.log("hi!");
            // console.log(`File "${fileName}" content: ${fileContent}`);
        };



        // Read the file as text
        reader.readAsText(file);
    }


});

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