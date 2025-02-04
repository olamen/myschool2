$(document).ready(function () {
    function updateSelectOptions(selectElement, data, defaultText) {
        selectElement.empty().append(`<option value="">${defaultText}</option>`);
        if (data && data.length > 0) {
            data.forEach(item => selectElement.append(`<option value="${item.id}">${item.name}</option>`));
        }
    }

    // Charger les matières et les classes quand le grade change
    $('#grade').change(function () {
        const gradeId = $(this).val();
        updateSelectOptions($('#subject'), [], "Sélectionnez une matière");
        updateSelectOptions($('#classe'), [], "Sélectionnez une classe");

        if (gradeId) {
            $.get(`/notes/get_subjects/${gradeId}/`, function (data) {
                if (data.success) updateSelectOptions($('#subject'), data.subjects, "Sélectionnez une matière");
            });

            $.get(`/notes/get_classes/${gradeId}/`, function (data) {
                if (data.success) updateSelectOptions($('#classe'), data.classes, "Sélectionnez une classe");
            });
        }
    });

    // Charger les exams quand le trimestre change
    $('#trimestre').change(function () {
        const trimestreId = $(this).val();
        updateSelectOptions($('#exam'), [], "Sélectionnez un exam");

        if (trimestreId) {
            $.get(`/notes/get_exams/${trimestreId}/`, function (data) {
                if (data.exams) updateSelectOptions($('#exam'), data.exams, "Sélectionnez un exam");
            });
        }
    });

    // Charger les étudiants quand la classe est sélectionnée
    $('#classe, #exam').change(function () {
        const classeId = $('#classe').val();
        const examId = $('#exam').val();

        if (classeId && examId) {
            $.get(`/notes/get_students/${classeId}/${examId}/`, function (data) {
                const studentsTable = $('#studentsTable');
                studentsTable.empty();
                data.students.forEach((student, index) => {
                    studentsTable.append(`
                        <tr>
                            <td>${index + 1}</td>
                            <td>${student.name}</td>
                            <td><input type="number" class="form-control student-score" data-student-id="${student.id}" min="0" max="20" step="0.1"></td>
                        </tr>
                    `);
                });
            });
        }
    });

    // Sauvegarde des notes
    $('#saveNotes').click(function () {
        let notes = [];
        $('.student-score').each(function () {
            let studentId = $(this).data('student-id');
            let score = $(this).val();
            if (score) notes.push({ student_id: studentId, score: score });
        });

        if (notes.length > 0) {
            let csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
            $.ajax({
                url: '/notes/notes_exam/save/',
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify({
                    notes: notes,
                    sessionyear: $('#sessionYear').val(),
                    subject_id: $('#subject').val(),
                    exam_id: $('#exam').val(),
                    trimestre_id: $('#trimestre').val()
                }),
                headers: { 'X-CSRFToken': csrfToken },
                success: function (response) { alert(response.message); },
                error: function (xhr) { alert(xhr.responseJSON?.message || "Erreur lors de l'enregistrement."); }
            });
        } else {
            alert("Veuillez entrer des notes pour les étudiants.");
        }
    });

    // Charger les notes existantes
    function loadNotes() {
        let params = {
            classe_id: $('#classe').val(),
            exam_id: $('#exam').val(),
            subject_id: $('#subject').val(),
            sessionyear_id: $('#sessionYear').val(),
            trimestre_id: $('#trimestre').val(),
            composition_id: $('#composition').val()
        };

        if (params.classe_id && params.subject_id && params.sessionyear_id && params.trimestre_id) {
            $.get('/notes/get_notes/', params, function (response) {
                if (response.success) {
                    $('.student-score').each(function () {
                        let studentId = $(this).data('student-id');
                        let note = response.notes.find(n => n.student_id == studentId);
                        if (note) $(this).val(note.score);
                    });
                }
            });
        }
    }

    // Recharger les notes quand une donnée change
    $('#classe, #exam, #subject, #sessionYear, #trimestre').change(function () {
        $('.student-score').val(''); // Réinitialisation des notes
        loadNotes();
    });
});