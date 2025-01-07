from django.db.models import Sum, F
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from notes.models import NoteComposition, NoteDevoir
from students.models import Student, Trimestre
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
def generate_report_card(request, student_id, trimestre_id):
    student = Student.objects.get(id=student_id)
    trimestre = Trimestre.objects.get(id=trimestre_id)

    # Calculate trimester scores with normalization to a scale of 20
    trimester_total_coefficient = NoteDevoir.objects.filter(
        student=student,
        trimestre=trimestre
    ).aggregate(Sum('coefficient'))['coefficient__sum'] or 1

    trimester_score_raw = calculate_cumulative_scores(student, trimestre)
    trimester_score = (trimester_score_raw / trimester_total_coefficient) * 20

    # Calculate yearly cumulative scores with normalization to a scale of 20
    yearly_total_coefficient = sum(
        NoteDevoir.objects.filter(
            student=student,
            trimestre=t
        ).aggregate(Sum('coefficient'))['coefficient__sum'] or 0
        for t in Trimestre.objects.filter(id__lte=trimestre.id)
    ) or 1

    yearly_score_raw = calculate_yearly_cumulative(student, trimestre)
    yearly_score = (yearly_score_raw / yearly_total_coefficient) * 20

    context = {
        'student': student,
        'trimestre': trimestre,
        'trimester_score': round(trimester_score, 2),  # Round to 2 decimals
        'yearly_score': round(yearly_score, 2),  # Round to 2 decimals
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