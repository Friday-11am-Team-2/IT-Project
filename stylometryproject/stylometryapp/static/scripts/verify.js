// Javascript for verification button (ONLY ON VERIFY)
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