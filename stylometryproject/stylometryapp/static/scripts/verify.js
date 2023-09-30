// Javascript for verification button (ONLY ON VERIFY)
document.addEventListener("DOMContentLoaded", () => {
    const runVerificationButton = document.getElementById("verify-button");

    let previousProfileID = 0;
    let previousProfileName = "";
    let previousFileName = "";

    // Check if the button has been clicked before by looking for a flag in local storage
    localStorage.setItem('buttonClicked', false);
    // const buttonClicked = localStorage.getItem('buttonClicked');
    // console.log(`Button Clicked: ${buttonClicked}`);

    // if (buttonClicked) {
    //     // If the button has been clicked before, disable it
    //     // runVerificationButton.disabled = true;
    // } else {
    //     runVerificationButton.disabled = false;
    // }

    if (runVerificationButton) {
        runVerificationButton.addEventListener("click", (event) => {

            event.preventDefault();
            var csrftoken = $('input[name=csrfmiddlewaretoken]').val();

            // Set a flag in local storage to indicate that the button has been clicked
            localStorage.setItem('buttonClicked', true);

            // Disable the button after clicking
            runVerificationButton.disabled = true;

            // Get profile ID from docDisplay
            const profileID = $('#curr-profile').data('profile-id');
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
                    "X-CSRFToken": csrftoken,
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
                    
                    currentProfileId = $('#curr-profile').data('profile-id')
                    currentProfileName =  $('#curr-profile').textContent

                    // Update previous
                    isNew = false;
                    if (previousProfileID !== profileID || previousFileName !== fileNamesArray[0]) {
                        previousProfileID = profileID;
                        previousProfileName = currentProfileName;
                        previousFileName = fileNamesArray[0];
                        isNew = true;
                    }

                    // Update the <p> field within the "verification-results" div
                    const verificationResultsParagraph = document.querySelector("#verification-results h3");
                    if (verificationResultsParagraph) {
                        verificationResultsParagraph.textContent = `${currentProfileName} vs ${fileNamesArray[0]}:`;
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