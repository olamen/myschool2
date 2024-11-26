from django.shortcuts import render
from django.http import HttpResponse
from .models import  ReportCard, Composition
from students.models import Student, Subject, Grade
from django.template.loader import get_template
from xhtml2pdf import pisa  # Utilisé pour générer des PDF

def exam_list(request):
    exams = Composition.objects.all()
    return render(request, "notes/exam_list.html", {"exams": exams})


def report_card_pdf(request, student_id, exam_id):
    student = Student.objects.get(id=student_id)
    exam = Composition.objects.get(id=exam_id)
    grades = Grade.objects.filter(student=student, exam=exam)

    total_score = sum(grade.get_weighted_score() for grade in grades)
    average_score = total_score / grades.count() if grades else 0

    context = {
        "student": student,
        "exam": exam,
        "grades": grades,
        "total_score": total_score,
        "average_score": round(average_score, 2),
    }

    template = get_template("notes/report_card.html")
    html = template.render(context)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f"attachment; filename=report_card_{student_id}_{exam_id}.pdf"

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("Error generating PDF")
    return response