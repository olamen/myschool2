from django.shortcuts import render
from django.http import HttpResponse
from .models import Grade, ReportCard, Exam
from students.models import Student, Subject
from django.template.loader import get_template
from xhtml2pdf import pisa  # Utilisé pour générer des PDF
from django.shortcuts import render, redirect, get_object_or_404
from students.models import Homework, Composition, Student, Subject
from django.http import HttpResponse

def exam_list(request):
    exams = Exam.objects.all()
    return render(request, "notes/exam_list.html", {"exams": exams})


def report_card_pdf(request, student_id, exam_id):
    student = Student.objects.get(id=student_id)
    exam = Exam.objects.get(id=exam_id)
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




# Homework CRUD
def homework_list(request):
    """List all homework."""
    homeworks = Homework.objects.all()
    return render(request, 'students/homework_list.html', {'homeworks': homeworks})

def add_homework(request):
    """Add new homework."""
    if request.method == 'POST':
        name = request.POST.get('name', 'Devoir')
        student_id = request.POST.get('student')
        subject_id = request.POST.get('subject')
        due_date = request.POST.get('due_date')
        description = request.POST.get('description')
        Homework.objects.create(
            name=name,
            student_id=student_id,
            subject_id=subject_id,
            due_date=due_date,
            description=description
        )
        return redirect('homework_list')
    students = Student.objects.all()
    subjects = Subject.objects.all()
    return render(request, 'notes/add_homework.html', {'students': students, 'subjects': subjects})

def edit_homework(request, pk):
    """Edit homework."""
    homework = get_object_or_404(Homework, pk=pk)
    if request.method == 'POST':
        homework.name = request.POST.get('name', 'Devoir')
        homework.student_id = request.POST.get('student')
        homework.subject_id = request.POST.get('subject')
        homework.due_date = request.POST.get('due_date')
        homework.description = request.POST.get('description')
        homework.save()
        return redirect('notes:homework_list')
    students = Student.objects.all()
    subjects = Subject.objects.all()
    return render(request, 'notes/edit_homework.html', {'homework': homework, 'students': students, 'subjects': subjects})

def delete_homework(request, pk):
    """Delete homework."""
    homework = get_object_or_404(Homework, pk=pk)
    homework.delete()
    return redirect('notes:homework_list')

# Composition CRUD
def composition_list(request):
    """List all compositions."""
    compositions = Composition.objects.all()
    return render(request, 'notes/composition_list.html', {'compositions': compositions})

def add_composition(request):
    """Add new composition."""
    if request.method == 'POST':
        name = request.POST.get('name', 'Composition')
        student_id = request.POST.get('student')
        subject_id = request.POST.get('subject')
        exam_date = request.POST.get('exam_date')
        remarks = request.POST.get('remarks', '')
        Composition.objects.create(
            name=name,
            student_id=student_id,
            subject_id=subject_id,
            exam_date=exam_date,
            remarks=remarks
        )
        return redirect('notes:composition_list')
    students = Student.objects.all()
    subjects = Subject.objects.all()
    return render(request, 'notes/add_composition.html', {'students': students, 'subjects': subjects})

def edit_composition(request, pk):
    """Edit composition."""
    composition = get_object_or_404(Composition, pk=pk)
    if request.method == 'POST':
        composition.name = request.POST.get('name', 'Composition')
        composition.student_id = request.POST.get('student')
        composition.subject_id = request.POST.get('subject')
        composition.exam_date = request.POST.get('exam_date')
        composition.remarks = request.POST.get('remarks', '')
        composition.save()
        return redirect('notes:composition_list')
    students = Student.objects.all()
    subjects = Subject.objects.all()
    return render(request, 'notes/edit_composition.html', {'composition': composition, 'students': students, 'subjects': subjects})

def delete_composition(request, pk):
    """Delete composition."""
    composition = get_object_or_404(Composition, pk=pk)
    composition.delete()
    return redirect('notes:composition_list')