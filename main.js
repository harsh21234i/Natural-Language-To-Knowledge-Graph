function generateSummary() {
    const text = document.querySelector("textarea").value;
    fetch("/summarize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text })
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("summary").innerText = data.summary;
    });
}

function askQuestion() {
    const question = document.getElementById("question_input").value;
    const context = document.querySelector("textarea").value;
    fetch("/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, context })
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("answer").innerText = data.answer;
    });
}
