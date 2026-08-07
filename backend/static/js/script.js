// =============================
// Get HTML Elements
// =============================

const form = document.getElementById("evaluationForm");
const resultBox = document.getElementById("resultBox");

// =============================
// Form Submit Event
// =============================

form.addEventListener("submit", async function (event) {

    event.preventDefault();

    // Get Values

    const question = document.getElementById("question").value.trim();

    const response = document.getElementById("response").value.trim();

    const reference = document.getElementById("reference").value.trim();

    const source = document.getElementById("source").value.trim();


    // =============================
    // Validation
    // =============================

    if (question === "" || response === "") {

        resultBox.innerHTML =
            "<p style='color:red;'>Question and AI Response are required.</p>";

        return;
    }

    // =============================
    // Prepare JSON
    // =============================

    const requestData = {

        question: question,

        response: response,

        reference_answer: reference || null,

        source_document: source || null

    };

    try {

        resultBox.innerHTML = "Sending request...";

        // =============================
        // Call Backend API
        // =============================

        const apiResponse = await fetch(
            "http://127.0.0.1:8000/api/evaluate",
            {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(requestData)

            }
        );

        const data = await apiResponse.json();

        // =============================
        // Display Response
        // =============================

        resultBox.innerHTML = `

<h3>Backend Response</h3>

<p><strong>Status:</strong> ${data.status}</p>

<p><strong>Message:</strong> ${data.message}</p>

<hr>

<p><strong>Question:</strong></p>

<p>${data.data.question}</p>

<p><strong>AI Response:</strong></p>

<p>${data.data.response}</p>

<p><strong>Reference Answer:</strong></p>

<p>${data.data.reference_answer ?? "Not Provided"}</p>

<p><strong>Source Document:</strong></p>

<p>${data.data.source_document ?? "Not Provided"}</p>

`;

    }

    catch (error) {

        console.error(error);

        resultBox.innerHTML =

            "<p style='color:red;'>Unable to connect to backend.</p>";

    }

});