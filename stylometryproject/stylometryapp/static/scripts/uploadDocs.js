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
        let fileSize = (file.size / 1024).toFixed(2);

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
            const uint8Array = new Uint8Array(event.target.result);
            const chunkSize = 65536; // Choose an appropriate chunk size based on your data
            const chunks = [];
            
            for (let i = 0; i < uint8Array.length; i += chunkSize) {
              const chunk = uint8Array.subarray(i, i + chunkSize);
              const chunkString = String.fromCharCode.apply(null, chunk);
              chunks.push(chunkString);
            }
            
            const fileContent = btoa(chunks.join(''));
            console.log(fileContent.length);
                                

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


const submitButton = document.getElementById("submit-button");
if (submitButton) {
  submitButton.addEventListener("click", () => {
    csrftoken = document.getElementsByName("csrfmiddlewaretoken")[0].value;
    console.log(csrftoken);

    const profileID = $('#curr-profile').data('profile-id');

    if (profileID <= 0) {
      alert("Please select a profile first");
      return;
    }

    const totalDocuments = fileNamesArray.length;
    let successfulUploads = 0;

    // Prevent duplicate submissions
    submitButton.disabled = true;

    // Iterate through each document and send a separate request
    for (let i = 0; i < totalDocuments; i++) {
      const fileName = fileNamesArray[i].name;
      const fileContent = fileContentArray[i];

      if (!fileName || !fileContent) {
        continue; // Skip empty or invalid data
      }

      const dataToSend = {
        profile_id: profileID,
        file_names: [fileName],
        file_contents: [fileContent],
      };

      fetch("/add_profile_docs/", {
        method: "POST",
        headers: {
          "X-CSRFToken": csrftoken,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(dataToSend),
      })
        .then((response) => {
          if (response.ok) {
            successfulUploads++;

            if (successfulUploads === totalDocuments) {
              // Reload the page when all uploads are complete
              location.reload('/profile/');
            }
          } else {
            console.error(`Error uploading document ${fileName}`);
            submitButton.disabled = false;
          }
        })
        .catch((error) => {
          console.error(`Error uploading document ${fileName}: ${error}`);
          submitButton.disabled = false;
        });
    }
  });
}

