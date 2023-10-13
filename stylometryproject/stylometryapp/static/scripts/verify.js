// Javascript for verification button (ONLY ON VERIFY)
document.addEventListener("DOMContentLoaded", () => {
    const runVerificationButton = document.getElementById("verify-button");
    const verifyTextPlaceholder = document.getElementById("verify-text");
    const loadingSpinner = document.querySelector(".loader");
    const resultsBox = document.querySelector(".results-box");
    const passIcon = document.getElementById("pass-icon");
    const failIcon = document.getElementById("fail-icon");
    const resultsMsg = document.getElementById("results-message");

    const analyticsTable = document.getElementById("analytics-table");
    const analyticsTableBody = document.getElementById("analytics-table-body");

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

            // Hide the display of results when run verification is clicked
            resultsBox.style.display = "none";
            passIcon.style.display = "none";
            failIcon.style.display = "none";

            analyticsTable.style.display = "none";
            while (analyticsTableBody.firstChild) {
                // Clear the table contents
                analyticsTableBody.removeChild(analyticsTableBody.lastChild);
            }

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

            // loading animation
            verifyTextPlaceholder.classList.add("none");

            // Redundant code
            //const verificationResults = document.getElementById("verification-results");
            //const values = verificationResults.querySelectorAll("p");
            // Iterate through the "Value" fields and remove them (no longer needed)
            //values.forEach((field) => {
            //    if (field.textContent.startsWith("Value: ")) {
            //        field.remove();
            //    }
            //});

            loadingSpinner.classList.toggle("none");


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
                    // remove loader
                    loadingSpinner.classList.toggle("none");

                    // Handle the response data
                    console.log("Verification successful");
                    console.log("Result:", data.score);

                    currentProfileId = $('#curr-profile').data('profile-id')
                    currentProfileName = $('#curr-profile').textContent

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

                    // Set the result text display as appropriate
                    let resultValue = data.result;
                    if (resultValue) {
                        resultsMsg.textContent = "Pass!";
                        passIcon.style.display = "block";
                    } else {
                        resultsMsg.textContent = "Fail!";
                        failIcon.style.display = "block";
                    }
                    resultsBox.style.display = "block";
                    console.log("Diplaying Results!");


                    // Display analytics
                    function generate_row(name, f1, f2, f3) {
                        var table_row = document.createElement("tr")

                        var heading = document.createElement("th")
                        heading.textContent = name
                        table_row.appendChild(heading)

                        var field = document.createElement("td")
                        field.textContent = f1
                        table_row.appendChild(field)

                        field = document.createElement("td")
                        field.textContent = f2
                        table_row.appendChild(field)

                        field = document.createElement("td")
                        field.textContent = f3
                        table_row.appendChild(field)

                        return table_row
                    }

                    analyticsTableBody.appendChild(generate_row("Known", data.k_rare_words, data.k_long_words, data.k_sent_len))
                    analyticsTableBody.appendChild(generate_row("Unknown", data.u_rare_words, data.u_long_words, data.u_sent_len))

                    analyticsTable.style.display = "block"

                    // Get Data Fields(redundant)
                    //const results = document.createElement("strong");
                    //results.textContent = finalResult;
                    //const newField = document.createElement("p");
                    //newField.appendChild(document.createTextNode("Value: "));
                    //newField.appendChild(results);






                    // Check if 'isNew' is true (redundant)
                    //if (isNew) {
                    //    // If 'isNew' is true, clear previous "Value" fields
                    //    const verificationResultsDiv = document.getElementById("verification-results");
                    //    const valueFields = verificationResultsDiv.querySelectorAll("p");

                    // Iterate through the "Value" fields and remove them
                    //valueFields.forEach((field) => {
                    //    if (field.textContent.startsWith("Value: ")) {
                    //        field.remove();
                    //    }
                    //});
                    //}
                    //document.getElementById("verification-results").appendChild(newField);
                })
                .catch((error) => {
                    // Hide the loading message when there's an error
                    loadingSpinner.classList.toggle("none");

                    console.log(error.message)
                    alert(error.message);
                });
        });
    }
});