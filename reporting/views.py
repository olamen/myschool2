from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from .models import  ReportCard
from students.models import Student, Composition, Grade
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required

from xhtml2pdf import pisa  # Utilisé pour générer des PDF

@login_required
def exam_list(request):
    exams = Composition.objects.all()
    return render(request, "reporting/exam_list.html", {"exams": exams})


def report_card_pdf(request, student_id, exam_id):
    # Retrieve the student and the exam (composition)
    student = get_object_or_404(Student, id=student_id)
    exam = get_object_or_404(Composition, id=exam_id)

    # Retrieve the corresponding report card
    report_card = get_object_or_404(ReportCard, student=student, exam=exam)

    # Retrieve the session year
    session_year = report_card.sessionyear

    context = {
        "student": student,
        "exam": exam,
        "report_card": report_card,
        "session_year": session_year,
    }

    # Render the report card template
    template = get_template("reporting/report_card_exam.html")
    html = template.render(context)

    # Generate the PDF response
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f"attachment; filename=report_{student.first_name}_{student.last_name}_{exam.name}.pdf"

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("Error generating PDF")
    return response