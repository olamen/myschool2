from django.http import JsonResponse
from django.shortcuts import render
from students.models import  Classe, Subject, Trimestre, SessionYearModel
from notes.models import NoteDevoir

def print_notes(request):
    classe_id = request.GET.get("classe")
    devoir_id = request.GET.get("devoir")
    trimestre_id = request.GET.get("trimestre")
    subject_id = request.GET.get("subject")
    session_year_id = request.GET.get("session_year")

    # Validate the required fields
    if not any([classe_id, devoir_id, trimestre_id, subject_id, session_year_id]):
        return JsonResponse({"success": False, "message": "Données manquantes"})

    # Query the data based on provided filters
    notes = NoteDevoir.objects.all()

    if classe_id:
        notes = notes.filter(student__student_class_id=classe_id)
    if devoir_id:
        notes = notes.filter(devoir_id=devoir_id)
    if trimestre_id:
        notes = notes.filter(trimestre_id=trimestre_id)
    if subject_id:
        notes = notes.filter(subject_id=subject_id)
    if session_year_id:
        notes = notes.filter(sessionyear_id=session_year_id)

    if not notes.exists():
        return JsonResponse({"success": False, "message": "Aucune note trouvée pour les filtres sélectionnés."})

    # Render the printable page
    return render(request, 'reporting/print_notes.html', {
        'notes': notes,
        'school_name_ar': "اسم المدرسة بالعربية",
        'school_name_fr': "Nom de l'école en français",
        'devoir': notes.first().devoir if devoir_id else None,
    })