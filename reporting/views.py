from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from .models import  ReportCard, Composition
from students.models import SessionYearModel, Student, Subject, Grade
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required

from xhtml2pdf import pisa  # Utilisé pour générer des PDF

def exam_list(request):
    exams = Composition.objects.all()
    return render(request, "reporting/exam_list.html", {"exams": exams})

@login_required
def report_card_pdf(request, student_id, exam_id):
    # Fetch the student and exam
    student = get_object_or_404(Student, id=student_id)
    exam = get_object_or_404(Composition, id=exam_id)

    # Fetch the grade of the student's class
    student_grade = student.student_class.grade

    # Filter compositions (or grades) for this student and this exam
    compositions = Composition.objects.filter(student=student, subject__class_enrolled=student.student_class)

    # Calculate total and average scores
    total_score = sum(comp.get_weighted_score() for comp in compositions)
    average_score = total_score / compositions.count() if compositions.exists() else 0

    context = {
        "student": student,
        "exam": exam,
        "compositions": compositions,
        "grade": student_grade,
        "total_score": total_score,
        "average_score": round(average_score, 2),
    }

    # Render HTML to PDF
    template = get_template("reporting/report_card_exam.html")
    html = template.render(context)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f"attachment; filename=report_{student.first_name}_{student.last_name}_{student_id}_{exam.name}.pdf"

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("Error generating PDF")
    return response