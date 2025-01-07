from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse

from notes.models import NoteComposition, NoteDevoir
from .models import  ReportCard
from students.models import Classe, Devoir, SessionYearModel, Student, Composition, Subject, Trimestre
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required

from xhtml2pdf import pisa  # Utilisé pour générer des PDF

@login_required
def afficher_notes_devoir(request):
    classes = Classe.objects.all()
    trimestres = Trimestre.objects.all()
    subjects = Subject.objects.all()
    session_years = SessionYearModel.objects.all()
    devoirs = Devoir.objects.all()

    # Récupération des filtres depuis les paramètres GET
    classe_id = request.GET.get('classe')
    trimestre_id = request.GET.get('trimestre')
    subject_id = request.GET.get('subject')
    sessionyear_id = request.GET.get('sessionyear')
    devoir_id= request.GET.get('devoir')

    # Filtrage des notes
    notes = NoteDevoir.objects.all()

    if classe_id:
        # Filtrer les notes par classe via l'étudiant
        notes = notes.filter(student__student_class_id=classe_id)
    if trimestre_id:
        notes = notes.filter(trimestre_id=trimestre_id)
    if subject_id:
        notes = notes.filter(subject_id=subject_id)
    if sessionyear_id:
        notes = notes.filter(sessionyear_id=sessionyear_id)
    if devoir_id:
        notes = notes.filter(devoir_id=devoir_id)

    context = {
        'classes': classes,
        'trimestres': trimestres,
        'subjects': subjects,
        'session_years': session_years,
        'devoirs':devoirs,
        'notes': notes,
    }
    return render(request, 'reporting/afficher_notes_devoir_list.html', context)

@login_required
def afficher_notes_exam(request):
    classes = Classe.objects.all()
    trimestres = Trimestre.objects.all()
    subjects = Subject.objects.all()
    session_years = SessionYearModel.objects.all()
    exams = NoteComposition.objects.all()

    # Récupération des filtres depuis les paramètres GET
    classe_id = request.GET.get('classe')
    trimestre_id = request.GET.get('trimestre')
    subject_id = request.GET.get('subject')
    session_year_id = request.GET.get('session_year')
    exam_id= request.GET.get('exam')

    # Filtrage des notes
    notes = NoteComposition.objects.all()

    if classe_id:
        # Filtrer les notes par classe via l'étudiant
        notes = notes.filter(student__student_class_id=classe_id)
    if trimestre_id:
        notes = notes.filter(trimestre_id=trimestre_id)
    if subject_id:
        notes = notes.filter(subject_id=subject_id)
    if session_year_id:
        notes = notes.filter(sessionyear_id=session_year_id)
    if exam_id:
        notes = notes.filter(exam_id=exam_id)

    context = {
        'classes': classes,
        'trimestres': trimestres,
        'subjects': subjects,
        'session_years': session_years,
        'exams':exams,
        'notes': notes,
    }
    return render(request, 'reporting/afficher_notes_exam_list.html', context)


@login_required
def exam_list(request):
    exams = NoteComposition.objects.select_related('student', 'subject','composition').all()
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