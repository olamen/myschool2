console.log("quiz.js loaded");

const modalBtns = document.querySelectorAll(".modal-button");
const modalBody = document.getElementById('modal-body-confirm')
const startQuizBtn = document.getElementById('start-button');
const url = window.location.href;

// NodeList supports forEach directly
modalBtns.forEach(modalBtn => {
    modalBtn.addEventListener("click", () => {
        const pk = modalBtn.getAttribute("data-pk");
        const name = modalBtn.getAttribute("data-quiz");
        const numberquestios = modalBtn.getAttribute("data-questions");
        const difficulty = modalBtn.getAttribute("data-difficulty");
        const data_required_score_to_pass = modalBtn.getAttribute("data-required_score_to_pass");
        const time_limit = modalBtn.getAttribute("data-time");
        console.log("pk: ", pk);
        console.log("name: ", name);
        console.log("number of questions: ", numberquestios);
        modalBody.innerHTML = `<div class="modal-body">
            <p>Are you sure you want to begin the quiz <strong>${name}</strong>?</p>
            <p>Number of questions: <strong>${numberquestios}</strong></p>
            <p>Difficulty: <strong>${difficulty}</strong></p>
            <p>Required score to pass: <strong>${data_required_score_to_pass}</strong></p>
            <p>Time limit: <strong>${time_limit} Minutes</strong></p></div>`;

        startQuizBtn.addEventListener("click", () => {
        window.location.href = `${url}${pk}`;
    });
});
});
