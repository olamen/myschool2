
from notes.models import  NoteDevoir
from django.contrib.auth.decorators import login_required

from xhtml2pdf import pisa  # Utilisé pour générer des PDF

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from students.models import  Devoir, Student, SessionYearModel, Classe, Subject, Trimestre
from django.template.loader import render_to_string

@login_required
def print_notes(request):
    classe_id = request.GET.get("classe_id")
    devoir_id = request.GET.get("devoir_id")
    subject_id = request.GET.get("subject_id")
    sessionyear_id = request.GET.get("sessionyear_id")
    trimestre_id = request.GET.get("trimestre_id")

    # Validate input
    if not all([classe_id, subject_id, sessionyear_id, trimestre_id]):
        return JsonResponse({"success": False, "message": "Données manquantes"})

    # Retrieve filtered notes
    students = Student.objects.filter(student_class_id=classe_id)
    notes = NoteDevoir.objects.filter(
        student__in=students,
        subject_id=subject_id,
        sessionyear_id=sessionyear_id,
        trimestre_id=trimestre_id,
    )

    # Retrieve related objects for the header
    school_name_ar = "مدرستي"  # Replace with your school name in Arabic
    school_name_fr = "Mon École"  # Replace with your school name in French
    devoir = get_object_or_404(Devoir, id=devoir_id) if devoir_id else None

    context = {
        "school_name_ar": school_name_ar,
        "school_name_fr": school_name_fr,
        "devoir": devoir,
        "notes": notes,
    }

    return render(request, "notes/print/print_notes.html", context)