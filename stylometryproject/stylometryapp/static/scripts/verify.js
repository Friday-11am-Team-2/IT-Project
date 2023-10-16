// Javascript for verification button (ONLY ON VERIFY)
document.addEventListener("DOMContentLoaded", () => {
    const runVerificationButton = document.getElementById("verify-button");
    const verifyTextPlaceholder = document.getElementById("verify-text");
    const loadingSpinner = document.querySelector(".loader");
    const resultsBox = document.querySelector(".results-box");
    const passIcon = document.getElementById("pass-icon");
    const failIcon = document.getElementById("fail-icon");
    const showModal = document.getElementById("show-modal");
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

            // analyticsTable.style.display = "none";
            // while (analyticsTableBody.firstChild) {
            //     // Clear the table contents
            //     analyticsTableBody.removeChild(analyticsTableBody.lastChild);
            // }

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
            loadingSpinner.classList.toggle("none");

            // don't show additional text until results loaded
            showModal.classList.add("none");

            // Redundant code
            //const verificationResults = document.getElementById("verification-results");
            //const values = verificationResults.querySelectorAll("p");
            // Iterate through the "Value" fields and remove them (no longer needed)
            //values.forEach((field) => {
            //    if (field.textContent.startsWith("Value: ")) {
            //        field.remove();
            //    }
            //});


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

                    // let currentProfileId = $('#curr-profile').data('profile-id')
                    let currentProfileName = $('#curr-profile').text()


                    // Update previous
                    // isNew = false;
                    // if (previousProfileID !== profileID || previousFileName !== fileNamesArray[0]) {
                    //     previousProfileID = profileID;
                    //     previousProfileName = currentProfileName;
                    //     previousFileName = fileNamesArray[0];
                    //     isNew = true;
                    // }

                    // // Update the <p> field within the "verification-results" div
                    // const verificationResultsParagraph = document.querySelector("#verification-results p");
                    // if (verificationResultsParagraph) {
                    //     verificationResultsParagraph.textContent = `${currentProfileName} vs ${fileNamesArray[0]}:`;
                    // }

                    // Set the result text display as appropriate
                    let resultValue = data.result;
                    if (resultValue) {
                        resultsMsg.textContent = fileNamesArray[0] + " is likely to be written by " + currentProfileName;
                        passIcon.style.display = "block";
                    } else {
                        resultsMsg.textContent = fileNamesArray[0] + " is unlikely to be written by " + currentProfileName;
                        failIcon.style.display = "block";
                    }
                    resultsBox.style.display = "block";
                    showModal.classList.remove("none");
                    console.log("Diplaying Results!");

                    displayAnalytics(resultValue ? true : false);
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

function displayAnalytics(pass) {
    const introText = document.getElementById("intro");
    const curProfile = $('#curr-profile').data('profile-id');
    const curProfileName = $('#curr-profile').text()
    const csrftoken = $('input[name=csrfmiddlewaretoken]').val();
    const unknown_name = fileNamesArray[0]

    const fetch_k = fetch("/text_analytics/?p=" + curProfile, {
        method: "POST",
        headers: {
            "X-CSRFToken": csrftoken,
            "Content-Type": "application/json",

        },
    })

    const fetch_u = fetch("/text_analytics/?l=1", {
        method: "POST",
        headers: {
            "X-CSRFToken": csrftoken,
            "Content-Type": "application/json",
        }
    }).then((response) => {
        if (!response.ok) {
            throw new Error("Analytics fetch failed!")
        }
        return response
    }).catch((error) => {
        // Fallback request that re-uploads the file content.
        // Very unlikely to be needed, but the server cache *could* be cleared in the time.
        response = fetch("/text_analytics/?f=" + fileNamesArray[0], {
            method: "GET",
            headers: {
                "X-CSRFToken": csrftoken,
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                file_names: fileNamesArray[0],
                file_contents: fileContentArray[0]
            })
        })
        return response
    })

    Promise.all([fetch_k, fetch_u]).then(responses => {
        const [res_k, res_u] = responses

        if (!res_k && res_u) {
            throw new Error("Fetching analytics failed!")
        }

        return Promise.all([res_k.json(), res_u.json()])
    }).then((data) => {
        const [known, unknown] = data

        if (pass) {
            introText.innerHTML = `Based on our authorship verification algorithm, the features of document: <i><u>${unknown_name}</u></i> <b>successfully correspond</b> to the profile: <i><u>${curProfileName}</u></i>.<br>
            Note - This result is calculated based on our algorithm that utilises stylistic analysis of the profile and document and should not be taken as a definite pass/fail.`
        } else {
            introText.innerHTML = `Based on our authorship verification algorithm, the features of document: <i><u>${unknown_name}</u></i> <b>do not correspond</b> the profile: <i><u>${curProfileName}</u></i>.<br>
            Note - This result is calculated based on our algorithm that utilises stylistic analysis of the profile and document and should not be taken as a definite pass/fail.`
        }

        drawGraph(known.rare_words, unknown.rare_words, 'Rare', true, curProfileName, unknown_name);
        drawGraph(known.rare_words, unknown.rare_words, 'Long', false, curProfileName, unknown_name);
        drawPieChart(known.sentence_avg, unknown.sentence_avg, curProfileName, unknown_name, "Sentence");
        drawPieChart(known.word_len_avg, unknown.word_len_avg, curProfileName, unknown_name, "Word");
    }).catch((error) => {
        console.log(error.message);
        alert(error.message);
        // TODO: This would be the place to add a more graceful response
        // to the server not replying.
    });
};

function drawGraph(knownMetric, unknownMetric, metric, legendBool, known, unknown) {
    let chartStatus = Chart.getChart(metric); // <canvas> id
    if (chartStatus != undefined) {
        chartStatus.destroy();
    };

    const knownPercent = (knownMetric) * 100
    const unknownPercent = (unknownMetric) * 100

    const dataset = [
        { label: `${metric} Words (%)`, value: Math.round(knownPercent * 10) / 10 },
        { label: `${metric} Words (%)`, value: Math.round(unknownPercent * 10) / 10 },
    ];

    const options = {
        indexAxis: 'y',
        plugins: {
            legend: {
                display: legendBool
            }
        },

        title: {
            display: false,
        },
        scales: {
            x: {
                suggestedMin: 0,
                suggestedMax: 100,
            }
        },
        maintainAspectRatio: false,

        scale: {
            pointLabels: {
                fontStyle: "bold"
            }
        }
    };
    const barWidth = 0.6;

    const graph = document.getElementById(metric);

    new Chart(graph, {
        type: "bar",
        data: {
            labels: [`${metric} Words (%)`],
            datasets: [
                {
                    label: known,
                    data: [dataset[0].value],
                    backgroundColor: '#FF5733',
                    barPercentage: barWidth,
                    minBarLength: 3,
                },
                {
                    label: unknown,
                    data: [dataset[1].value],
                    backgroundColor: '#FFC300',
                    barPercentage: barWidth,
                    minBarLength: 3,
                }
            ]
        },
        options: options,
    });
}

function drawPieChart(k_data1, u_data1, known, unknown, metric) {
    let chartStatus = Chart.getChart(`${metric}-Pie`); // <canvas> id
    if (chartStatus != undefined) {
        chartStatus.destroy();
    };

    var data = {
        labels: [
            known,
            unknown,
        ],
        datasets: [{
            data: [k_data1, u_data1],
            backgroundColor: ["#FF5733", "#FFC300"]
        }]
    }

    const ctx = document.getElementById(`${metric}-Pie`);

    new Chart(ctx, {
        type: 'pie',
        data: data,
        options: {
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: `Average ${metric} Length`,
                    font: {
                        size: 14,
                        weight: 700,
                    },
                }
            },
            maintainAspectRatio: false,
        },
    });
}