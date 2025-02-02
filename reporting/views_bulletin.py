from django.db.models import Sum, F, Case, When
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from notes.models import NoteComposition, NoteDevoir
from students.models import Student, Subject, Trimestre,SessionYearModel
from weasyprint import HTML
from django.template.loader import render_to_string


def calculate_cumulative_scores(student, trimestre):
    """
    Calculate cumulative scores for a student in a specific trimester.
    """
    # Get assignments and their weighted scores
    assignments = NoteDevoir.objects.filter(
        student=student,
        trimestre=trimestre
    ).annotate(weighted_score=F('score') * F('coefficient'))

    assignment_total = assignments.aggregate(Sum('weighted_score'))['weighted_score__sum'] or 0

    # Get the exam score and its weighted value
    exam = NoteComposition.objects.filter(
        student=student,
        trimestre=trimestre
    ).first()

    exam_total = (exam.score * exam.coefficient) if exam else 0

    return assignment_total + exam_total

def calculate_yearly_cumulative(student, trimestre):
    """
    Calculate the cumulative score for the year up to a specific trimester.
    """
    trimesters = Trimestre.objects.filter(id__lte=trimestre.id)
    cumulative_score = 0

    for t in trimesters:
        cumulative_score += calculate_cumulative_scores(student, t)

    return cumulative_score


@login_required
def generate_report_card(request, student_id, trimestre_id, sessionyear_id):
    student = Student.objects.get(id=student_id)
    trimestre = Trimestre.objects.get(id=trimestre_id)
    session_year = SessionYearModel.objects.get(id=sessionyear_id)

    student_grade = student.student_class.grade.name.lower()

    subjects = NoteDevoir.objects.filter(student=student, trimestre=trimestre).values(
        'subject__name', 'subject__points', 'coefficient'
    ).annotate(
        total_score=Case(
            When(subject__grade__name__iexact='primaire', then=Sum('score')),
            default=Sum(F('score') * F('coefficient'))
        ),
        normalized_score=Case(
            When(
                subject__grade__name__iexact='primaire',
                then=Sum('score')
            ),
            default=(Sum(F('score') * F('coefficient')) / Sum('coefficient')) * 20
        )
    )

    if student_grade == 'primaire':
        trimester_total_raw_score = sum(
            NoteDevoir.objects.filter(student=student, trimestre=trimestre, subject__grade__name__iexact='primaire')
            .values_list('score', flat=True)
        )

        trimester_total_possible = sum(
            filter(None, Subject.objects.filter(grade__name__iexact='primaire').values_list('points', flat=True))
        ) or 1

        trimester_score = (trimester_total_raw_score / trimester_total_possible) * 20

        yearly_total_raw_score = sum(
            NoteDevoir.objects.filter(student=student, trimestre__id__lte=trimestre.id, subject__grade__name__iexact='primaire')
            .values_list('score', flat=True)
        )

        yearly_total_possible = sum(
            filter(None, Subject.objects.filter(grade__name__iexact='primaire').values_list('points', flat=True))
        ) or 1

        yearly_score = (yearly_total_raw_score / yearly_total_possible) * 20
    else:
        trimester_total_raw_score = calculate_cumulative_scores(student, trimestre)
        trimester_total_coefficient = NoteDevoir.objects.filter(student=student, trimestre=trimestre).aggregate(
            total_coefficient=Sum('coefficient')
        )['total_coefficient'] or 1
        trimester_score = (trimester_total_raw_score / trimester_total_coefficient) * 20

        yearly_total_raw_score = calculate_yearly_cumulative(student, trimestre)
        yearly_total_coefficient = sum(
            NoteDevoir.objects.filter(student=student, trimestre=t).aggregate(Sum('coefficient'))['coefficient__sum'] or 0
            for t in Trimestre.objects.filter(id__lte=trimestre.id)
        ) or 1
        yearly_score = (yearly_total_raw_score / yearly_total_coefficient) * 20

    context = {
        'student': student,
        'trimestre': trimestre,
        'subjects': subjects,
        'session_year': session_year,
        'trimester_score': round(trimester_score, 2),
        'yearly_score': round(yearly_score, 2),
    }

    return render(request, 'reporting/report_card.html', context)

def generate_class_report_cards(request, classe_id, trimestre_id):
    students = Student.objects.filter(student_class_id=classe_id)
    trimestre = Trimestre.objects.get(id=trimestre_id)

    report_cards = []

    for student in students:
        trimester_score = calculate_cumulative_scores(student, trimestre)
        yearly_score = calculate_yearly_cumulative(student, trimestre)
        report_cards.append({
            'student': student,
            'trimester_score': trimester_score,
            'yearly_score': yearly_score,
        })

    context = {
        'report_cards': report_cards,
        'trimestre': trimestre,
    }

    return render(request, 'reporting/class_report_cards.html', context)


def generate_pdf_report_card(request, student_id, trimestre_id):
    student = Student.objects.get(id=student_id)
    trimestre = Trimestre.objects.get(id=trimestre_id)
    trimester_score = calculate_cumulative_scores(student, trimestre)
    yearly_score = calculate_yearly_cumulative(student, trimestre)

    html_string = render_to_string('reporting/report_card.html', {
        'student': student,
        'trimestre': trimestre,
        'trimester_score': trimester_score,
        'yearly_score': yearly_score,
    })

    pdf = HTML(string=html_string).write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="bulletin_{student.last_name}.pdf"'
    return response


@login_required
def generate_final_report_card(request, student_id, sessionyear_id):
    """
    Génère le bulletin final des étudiants (hors primaire).
    """
    student = get_object_or_404(Student, id=student_id)
    session_year = get_object_or_404(SessionYearModel, id=sessionyear_id)

    # Vérifier si l'étudiant est en primaire
    if student.student_class.grade.name.lower() == "primaire":
        return render(request, 'reporting/not_allowed.html', {"message": "Les élèves du primaire ne sont pas concernés."})

    # Récupérer les trimestres de l'année scolaire
    trimestres = Trimestre.objects.filter(session_year=session_year)

    # Récupérer les matières
    subjects = Subject.objects.filter(grade=student.student_class.grade)

    results = []
    total_yearly_score = 0
    total_coefficient = 0

    for subject in subjects:
        subject_result = {"subject": subject.name, "trimesters": []}
        subject_total_score = 0
        subject_total_coefficient = 0

        for trimestre in trimestres:
            # Calculer la note du devoir
            devoirs = NoteDevoir.objects.filter(student=student, subject=subject, trimestre=trimestre)
            devoir_score = devoirs.aggregate(total=Sum(F('score') * F('coefficient')))['total'] or 0

            # Calculer la note de composition
            composition = NoteComposition.objects.filter(student=student, subject=subject, trimestre=trimestre).first()
            composition_score = (composition.score * composition.coefficient) if composition else 0

            # Total du trimestre pour la matière
            trimestre_total = devoir_score + composition_score
            coefficient = subject.coefficient if subject.coefficient else 1

            subject_result["trimesters"].append({
                "trimestre": trimestre.name,
                "score": trimestre_total,
                "coefficient": coefficient,
                "normalized_score": (trimestre_total / coefficient) * 20 if coefficient else 0
            })

            subject_total_score += trimestre_total
            subject_total_coefficient += coefficient

        # Calcul de la moyenne annuelle de la matière
        yearly_score = (subject_total_score / subject_total_coefficient) * 20 if subject_total_coefficient else 0

        total_yearly_score += subject_total_score
        total_coefficient += subject_total_coefficient

        subject_result["yearly_score"] = yearly_score
        results.append(subject_result)

    # Calcul de la moyenne générale annuelle
    yearly_average = (total_yearly_score / total_coefficient) * 20 if total_coefficient else 0

    context = {
        "student": student,
        "session_year": session_year,
        "trimestres": trimestres,
        "results": results,
        "yearly_average": round(yearly_average, 2)
    }

    return render(request, "reporting/final_report_card.html", context)