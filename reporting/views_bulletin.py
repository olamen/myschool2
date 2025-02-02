from django.db.models import Sum, F, Case, When, FloatField
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from notes.models import NoteComposition, NoteDevoir
from students.models import Student, Subject, Trimestre, SessionYearModel
from weasyprint import HTML
from django.template.loader import render_to_string
from itertools import chain


def calculate_cumulative_scores(student, trimestre):
    """
    Calcule le score cumulé (devoir + composition) pour un étudiant sur un trimestre.
    """
    # Somme pondérée des devoirs
    devoirs = NoteDevoir.objects.filter(student=student, trimestre=trimestre).aggregate(
        total=Sum(F('score') * F('coefficient'), output_field=FloatField())
    )['total'] or 0

    # Score pondéré de la composition
    composition = NoteComposition.objects.filter(student=student, trimestre=trimestre).first()
    composition_score = (composition.score * composition.coefficient) if composition else 0

    return devoirs + composition_score

def calculate_yearly_cumulative(student, trimestre):
    """
    Calcule le score cumulé annuel jusqu'à un trimestre donné.
    """
    return sum(calculate_cumulative_scores(student, t) for t in Trimestre.objects.filter(id__lte=trimestre.id))

@login_required
def generate_report_card(request, student_id, trimestre_id, sessionyear_id):
    student = get_object_or_404(Student, id=student_id)
    trimestre = get_object_or_404(Trimestre, id=trimestre_id)
    session_year = get_object_or_404(SessionYearModel, id=sessionyear_id)
    student_grade = student.student_class.grade.name.lower()

    subjects = Subject.objects.filter(grade=student.student_class.grade)
    results = []

    total_trimester_score = 0
    total_trimester_coefficient = 0

    for subject in subjects:
        # Calcul des notes de devoir et composition
        devoirs = NoteDevoir.objects.filter(student=student, subject=subject, trimestre=trimestre).aggregate(
            total=Sum(F('score') * F('coefficient'), output_field=FloatField())
        )['total'] or 0

        composition = NoteComposition.objects.filter(student=student, subject=subject, trimestre=trimestre).first()
        composition_score = (composition.score * composition.coefficient) if composition else 0

        # Score total du trimestre pour la matière
        total_score = devoirs + composition_score
        coefficient = subject.coefficient if subject.coefficient else 1

        total_trimester_score += total_score
        total_trimester_coefficient += coefficient

        results.append({
            "subject": subject.name,
            "devoirs": round(devoirs, 2),
            "composition": round(composition_score, 2),
            "total": round(total_score, 2),
            "coefficient": coefficient,
            "normalized_score": round((total_score / coefficient) * 20 if coefficient else 0, 2),
        })

    trimester_score = round((total_trimester_score / total_trimester_coefficient) * 20 if total_trimester_coefficient else 0, 2)
    yearly_score = round((calculate_yearly_cumulative(student, trimestre) / total_trimester_coefficient) * 20 if total_trimester_coefficient else 0, 2)

    context = {
        "student": student,
        "trimestre": trimestre,
        "session_year": session_year,
        "results": results,
        "trimester_score": trimester_score,
        "yearly_score": yearly_score,
    }

    return render(request, "reporting/report_card.html", context)

@login_required
def generate_final_report_card(request, student_id, sessionyear_id):
    """
    Génère le bulletin final des étudiants (hors primaire).
    """
    student = get_object_or_404(Student, id=student_id)
    session_year = get_object_or_404(SessionYearModel, id=sessionyear_id)

    if student.student_class.grade.name.lower() == "primaire":
        return render(request, 'reporting/not_allowed.html', {"message": "Les élèves du primaire ne sont pas concernés."})

    # Récupérer les trimestres liés aux NotesDevoir
    trimestres_devoirs = Trimestre.objects.filter(
        id__in=NoteDevoir.objects.filter(sessionyear=session_year).values_list('trimestre', flat=True)
    )

    # Récupérer les trimestres liés aux NotesComposition
    trimestres_compositions = Trimestre.objects.filter(
        id__in=NoteComposition.objects.filter(sessionyear=session_year).values_list('trimestre', flat=True)
    )

    # Fusionner les deux QuerySets en une liste unique et éliminer les doublons
    trimestres = list(set(chain(trimestres_devoirs, trimestres_compositions)))
    subjects = Subject.objects.filter(grade=student.student_class.grade)

    results = []
    total_yearly_score = 0
    total_coefficient = 0

    for subject in subjects:
        subject_result = {"subject": subject.name, "trimesters": []}
        subject_total_score = 0
        subject_total_coefficient = 0

        for trimestre in trimestres:
            devoirs = NoteDevoir.objects.filter(student=student, subject=subject, trimestre=trimestre).aggregate(
                total=Sum(F('score') * F('coefficient'), output_field=FloatField())
            )['total'] or 0

            composition = NoteComposition.objects.filter(student=student, subject=subject, trimestre=trimestre).first()
            composition_score = (composition.score * composition.coefficient) if composition else 0

            trimestre_total = devoirs + composition_score
            coefficient = subject.coefficient if subject.coefficient else 1

            subject_result["trimesters"].append({
                "trimestre": trimestre.name,
                "score": round(float(trimestre_total), 2),
                "coefficient": coefficient,
                "normalized_score": round((float(trimestre_total) / coefficient) * 20 if coefficient else 0, 2)
            })

            subject_total_score += float(trimestre_total)
            subject_total_coefficient += coefficient

        yearly_score = round((float(subject_total_score) / subject_total_coefficient) * 20 if subject_total_coefficient else 0, 2)
        total_yearly_score += float(subject_total_score)
        total_coefficient += subject_total_coefficient

        subject_result["yearly_score"] = yearly_score
        results.append(subject_result)

    yearly_average = round((float(total_yearly_score) / total_coefficient) * 20 if total_coefficient else 0, 2)

    context = {
        "student": student,
        "session_year": session_year,
        "trimestres": trimestres,
        "results": results,
        "yearly_average": yearly_average
    }

    return render(request, "reporting/final_report_card.html", context)


def generate_pdf_report_card(request, student_id, trimestre_id):
    student = get_object_or_404(Student, id=student_id)
    trimestre = get_object_or_404(Trimestre, id=trimestre_id)

    trimester_score = round(calculate_cumulative_scores(student, trimestre), 2)
    yearly_score = round(calculate_yearly_cumulative(student, trimestre), 2)

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