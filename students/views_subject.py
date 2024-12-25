from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Subject

# Liste des sujets
def subject_list(request):
    subjects = Subject.objects.all()
    return render(request, 'subjects/subject_list.html', {'subjects': subjects})

# Créer un sujet
def subject_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        coefficient = request.POST.get('coefficient')
        # Créer un nouveau sujet
        Subject.objects.create(name=name, coefficient=coefficient)
        messages.success(request, "Sujet créé avec succès !")
        return redirect('subject_list')
    return render(request, 'subjects/subject_form.html',)

# Modifier un sujet
def subject_update(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    if request.method == 'POST':
        subject.name = request.POST.get('name')
        subject.coefficient = request.POST.get('coefficient')
        subject.save()
        messages.success(request, "Sujet modifié avec succès !")
        return redirect('subject_list')

    return render(request, 'subjects/subject_form.html', {'subject': subject,})

# Activer/Désactiver un sujet
def subject_toggle_status(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    subject.is_active = not subject.is_active
    subject.save()
    status = "activé" if subject.is_active else "désactivé"
    messages.success(request, f"Sujet {status} avec succès !")
    return redirect('subject_list')