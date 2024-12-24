import json
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import  NoteComposition, Exam, NoteDevoir
from students.models import Classe, SessionYearModel, Student, Subject, Grade, Trimestre
from django.template.loader import get_template
from xhtml2pdf import pisa  # Utilisé pour générer des PDF
from django.shortcuts import render, redirect, get_object_or_404
from students.models import Devoir, Composition, Student, Subject
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required




@login_required
def ajouter_notes_devoir(request):
    session_years = SessionYearModel.objects.all()
    trimestres = Trimestre.objects.all()
    devoirs = Devoir.objects.all()
    subjects = Subject.objects.all()
    classes = Classe.objects.all()

    context = {
        'session_years': session_years,
        'trimestres': trimestres,
        'devoirs': devoirs,
        'subjects': subjects,
        'classes': classes,
    }
    return render(request, 'notes/ajouter_notes_devoir.html', context)

@login_required
def get_students(request, classe_id, devoir_id):
    print(f"Classe ID: {classe_id}, Devoir ID: {devoir_id}")  # Vérification
    classe = get_object_or_404(Classe, id=classe_id)
    # Récupérer les étudiants de cette classe via student_class
    students = Student.objects.filter(student_class=classe)
    # Préparer les données des étudiants
    students_data = [{"id": student.id, "name": f"{student.first_name} {student.last_name}"} for student in students]
    return JsonResponse({"students": students_data})

#save note devoir
@login_required
@csrf_exempt
def save_note_devoir(request):
    if request.method == 'POST':
        # Vérifiez les données reçues
        print("Données reçues :", request.body)  # Affiche les données brutes
        print("Données POST :", request.POST)    # Affiche les données parsées
        try:
            data = json.loads(request.body)
            notes = data.get('notes', [])

            for note_data in notes:
                student_id = note_data.get('student_id')
                subject_id = note_data.get('subject_id')
                classe_id = note_data.get('classe_id')
                sessionyear_id = note_data.get('sessionyear_id')
                trimestre_id = note_data.get('trimestre_id')
                devoir_id = note_data.get('devoir_id')
                score = note_data.get('score')

                if not all([student_id, subject_id, classe_id, sessionyear_id, trimestre_id, devoir_id, score]):
                    return JsonResponse({'success': False, 'message': 'Données manquantes.'}, status=400)

                student = get_object_or_404(Student, id=student_id)
                subject = get_object_or_404(Subject, id=subject_id)
                classe = get_object_or_404(Classe, id=classe_id)
                session_year = get_object_or_404(SessionYearModel, id=sessionyear_id)
                trimestre = get_object_or_404(Trimestre, id=trimestre_id)
                devoir = get_object_or_404(Devoir, id=devoir_id)

                if not 0 <= float(score) <= 20:
                    return JsonResponse({'success': False, 'message': f'Note invalide pour {student.first_name} {student.last_name}.'}, status=400)

                # Créer ou mettre à jour la note
                NoteDevoir.objects.update_or_create(
                    student=student,
                    subject=subject,
                    classe=classe,
                    sessionyear=session_year,
                    trimestre=trimestre,
                    exam=devoir,
                    defaults={
                        'coefficient': devoir.coefficient,
                        'score': float(score),
                    }
                )

            return JsonResponse({'success': True, 'message': 'Notes enregistrées avec succès !'})
        except Exception as e:
            print("Erreur :", str(e))  # Pour déboguer
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée.'}, status=405)

#old
def exam_list(request):
    exams = Exam.objects.all()
    return render(request, "notes/exam_list.html", {"exams": exams})



# Homework CRUD
def homework_list(request):
    """List all homework."""
    homeworks = Devoir.objects.all()
    return render(request, 'notes/homework_list.html', {'homeworks': homeworks})

def add_homework(request):
    """Add new homework."""
    if request.method == 'POST':
        name = request.POST.get('name', 'Devoir')
        student_id = request.POST.get('student')
        subject_id = request.POST.get('subject')
        due_date = request.POST.get('due_date')
        description = request.POST.get('description')
        Devoir.objects.create(
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
    homework = get_object_or_404(Devoir, pk=pk)
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
    homework = get_object_or_404(Devoir, pk=pk)
    homework.delete()
    return redirect('homework_list')

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
        return redirect('composition_list')
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
        return redirect('composition_list')
    students = Student.objects.all()
    subjects = Subject.objects.all()
    return render(request, 'notes/edit_composition.html', {'composition': composition, 'students': students, 'subjects': subjects})

def delete_composition(request, pk):
    """Delete composition."""
    composition = get_object_or_404(Composition, pk=pk)
    composition.delete()
    return redirect('composition_list')