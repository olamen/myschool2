console.log("quiz_main.js loaded");
document.addEventListener("DOMContentLoaded", () => {
    const url = window.location.href;
    const questionContainer = document.getElementById("question-container");
    const prevBtn = document.getElementById("prev-btn");
    const nextBtn = document.getElementById("next-btn");
    const debugLogs = document.getElementById("debug-logs");
    const timerElement = document.getElementById("timer"); // Timer element

    let currentQuestionIndex = 0;
    let questions = [];
    let userAnswers = {}; // Store user answers
    let timeRemaining = 0; // Time in seconds

    // Helper function to log debug messages
    function logDebug(message) {
        console.log(message); // Log to the console
        if (debugLogs) {
            debugLogs.textContent += `${message}\n`; // Append to the debug log element
        }
    }

    $.ajax({
        type: "GET",
        url: url + "data/",
        success: function (response) {
            console.log("Received Data:", response);
            questions = response.data.map((item) => {
                return {
                    id: item.id,
                    text: item.text,
                    answers: item.answers,
                };
            });

            timeRemaining = response.time * 60; // Convert minutes to seconds
            startTimer();

            if (questions.length > 0) {
                displayQuestion(currentQuestionIndex);
            } else {
                console.error("No questions available in the quiz.");
            }
        },
        error: function (error) {
            console.log("Error fetching quiz data: ", error);
        },
    });

    function displayQuestion(index) {
        if (!questions.length) {
            console.error("Questions array is empty.");
            return;
        }

        logDebug(`Displaying question ${index + 1}`);
        const question = questions[index];

        questionContainer.innerHTML = `
            <div class="mb-4">
                <h5>Question ${index + 1} of ${questions.length}</h5>
                <p><strong>${question.text}</strong></p>
            </div>
            <div>
                ${question.answers.map((answer, i) => `
                    <div class="form-check">
                        <input class="form-check-input ans" type="radio" name="question-${question.id}" id="answer-${i}" value="${answer.text}">
                        <label class="form-check-label radiocontainer" for="answer-${i}">${answer.text}</label>
                    </div>
                `).join("")}
            </div>
        `;

        prevBtn.disabled = index === 0;
        nextBtn.textContent = index === questions.length - 1 ? "Submit" : "Next";

        // Attach event listeners to store selected answers
        document.querySelectorAll(`input[name="question-${question.id}"]`).forEach((input) => {
            input.addEventListener("change", (e) => {
                userAnswers[`question-${question.id}`] = e.target.value; // Store answer
                logDebug(`Answer for question ${index + 1}: ${e.target.value}`);
            });
        });
    }

    function startTimer() {
        const timerInterval = setInterval(() => {
            if (timeRemaining <= 0) {
                clearInterval(timerInterval);
                alert("Time is up! Submitting your quiz...");
                sendData();
            } else {
                timeRemaining--;
                const minutes = Math.floor(timeRemaining / 60);
                const seconds = timeRemaining % 60;
    
                // Update the timer display
                timerElement.textContent = `Time Remaining: ${minutes}:${seconds < 10 ? "0" : ""}${seconds}`;
                
                // Apply Bootstrap alert styling
                timerElement.classList.remove("text-white", "text-warning");
                if (timeRemaining <= 15) {
                    timerElement.classList.add("text-danger", "bounce-animation");
                } else if (timeRemaining <= 30) {
                    timerElement.classList.add("text-warning");
                } else {
                    timerElement.classList.add("text-white",);
                }
            }
        }, 1000);
    }
    

    prevBtn.addEventListener("click", () => {
        if (currentQuestionIndex > 0) {
            currentQuestionIndex--;
            displayQuestion(currentQuestionIndex);
        }
        logDebug(`Navigated to previous question: ${currentQuestionIndex}`);
    });

    nextBtn.addEventListener("click", () => {
        logDebug("Next button clicked");
        if (currentQuestionIndex < questions.length - 1) {
            currentQuestionIndex++;
            displayQuestion(currentQuestionIndex);
        } else {
            logDebug("Quiz submitted!");
            sendData();
        }
    });

    function sendData() {
        const csrfTokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
        if (!csrfTokenElement) {
            console.error("CSRF token not found.");
            return;
        }

        const data = { csrfmiddlewaretoken: csrfTokenElement.value };

        Object.keys(userAnswers).forEach((key) => {
            data[key] = userAnswers[key];
        });

        console.log("Final Data Sent:", JSON.stringify(data)); // Debugging output

        $.ajax({
            type: "POST",
            url: url + "save/",
            contentType: "application/json",
            data: JSON.stringify(data),
            headers: { "X-CSRFToken": csrfTokenElement.value },
            success: function (response) {
                console.log("Data sent successfully:", response);
                // Redirect to the URL returned by the server
                window.location.href = response.redirect_url;
            },
            error: (error) => console.error("Error sending data:", error),
        });
    }

    document.getElementById("quiz-form").addEventListener("submit", (event) => {
        event.preventDefault();
        logDebug("Quiz form submitted");
        sendData();
    });
});
