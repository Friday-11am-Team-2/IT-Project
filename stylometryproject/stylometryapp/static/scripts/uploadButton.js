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
    fileNamesArray.length = [];
    fileContentArray.length = [];

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
}

document.addEventListener("DOMContentLoaded", () => {
    console.log("loading")
    const runVerificationButton = document.getElementById("verify-button");

    let previousProfileID = 0;
    let previousProfileName = "";
    let previousFileName = "";

    if (runVerificationButton) {
        runVerificationButton.addEventListener("click", (event) => {
            event.preventDefault();

            console.log("hello")
            
            // Get profile ID from docDisplay
            const profileID = uniqueCurrentProfileID;
            if (profileID <= 0) {
                alert("Please select a profile first");
                return;
            }

            if (fileNamesArray.length === 0) {
                alert("Please select files to verify");
                return;
            }

            // Send the data
            const dataToSend = {
                profile_id: profileID, // Add the profile ID to the JSON data
                file_names: fileNamesArray,
                file_contents: fileContentArray,
            };

            fetch("/run_verify/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(dataToSend), // Send the modified data
            })
                .then((response) => {
                    if (response.ok) {
                        return response.json(); // Parse the JSON response
                    } else {
                        throw new Error("Error fetching data from server (does profile have documents?)");
                    }
                })
                .then((data) => {
                    // Handle the response data
                    console.log("Verification successful");
                    console.log("Result:", data.result);

                    // Update previous
                    isNew = false;
                    if (previousProfileID !== profileID || previousFileName !== fileNamesArray[0]) {
                        previousProfileID = profileID;
                        previousProfileName = uniqueCurrentProfileName;    
                        previousFileName = fileNamesArray[0];
                        isNew = true;                
                    }

                    // Update the <p> field within the "verification-results" div
                    const verificationResultsParagraph = document.querySelector("#verification-results h3");
                    if (verificationResultsParagraph) {
                        verificationResultsParagraph.textContent = `${uniqueCurrentProfileName} vs ${fileNamesArray[0]}:`;
                    }

                    // Get Data Fields
                    const resultValue = document.createElement("strong");
                    resultValue.textContent = data.result;
                    
                    const newField = document.createElement("p");
                    newField.appendChild(document.createTextNode("Value: "));
                    newField.appendChild(resultValue);


                    // Check if 'isNew' is true
                    if (isNew) {
                        // If 'isNew' is true, clear previous "Value" fields
                        const verificationResultsDiv = document.getElementById("verification-results");
                        const valueFields = verificationResultsDiv.querySelectorAll("p");
                        
                        // Iterate through the "Value" fields and remove them
                        valueFields.forEach((field) => {
                            if (field.textContent.startsWith("Value: ")) {
                                field.remove();
                            }
                        });
                    }
                    document.getElementById("verification-results").appendChild(newField);
                })
                .catch((error) => {
                    console.log(error.message)
                    alert(error.message);
            });
        });
    }
});