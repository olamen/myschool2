from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Grade, Subject

# Liste des sujets
def subject_list(request):
    subjects = Subject.objects.all()
    return render(request, 'subjects/subject_list.html', {'subjects': subjects})

# Create or Update Subject
def subject_form(request, subject_id=None):
    subject = get_object_or_404(Subject, id=subject_id) if subject_id else None
    grades = Grade.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        grade_id = request.POST.get('grade')
        points = request.POST.get('points')
        coefficient = request.POST.get('coefficient')

        grade = get_object_or_404(Grade, id=grade_id)
        
        if not subject:
            subject = Subject(name=name, grade=grade)
        else:
            subject.name = name
            subject.grade = grade
        
        if grade.name.lower() == 'primaire':
            subject.points = points
            subject.coefficient = None
        else:
            subject.coefficient = coefficient
            subject.points = None

        subject.save()
        messages.success(request, "Sujet enregistré avec succès !")
        return redirect('subject_list')

    return render(request, 'subjects/subject_form.html', {'subject': subject, 'grades': grades})

# Activer/Désactiver un sujet
def subject_toggle_status(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    subject.is_active = not subject.is_active
    subject.save()
    status = "activé" if subject.is_active else "désactivé"
    messages.success(request, f"Sujet {status} avec succès !")
    return redirect('subject_list')