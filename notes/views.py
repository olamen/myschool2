from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import  NoteComposition, Exam, NoteDevoir
from students.models import Classe, SessionYearModel, Student, Subject, Grade
from django.template.loader import get_template
from xhtml2pdf import pisa  # Utilisé pour générer des PDF
from django.shortcuts import render, redirect, get_object_or_404
from students.models import Devoir, Composition, Student, Subject
from django.http import HttpResponse



def ajouter_notes_devoir(request):
    if request.method == "POST":
        # Récupération des données du formulaire
        sessionyear_id = request.POST.get("sessionyear")
        devoir_id = request.POST.get("devoir")
        classe_id = request.POST.get("classe")
        subject_id = request.POST.get("subject")

        # Récupérer les étudiants de la classe sélectionnée
        classe = get_object_or_404(Classe, id=classe_id)
        students = classe.students.all()

        # Mise à jour des notes
        for student in students:
            score = request.POST.get(f"score_{student.id}")  # Récupère la note entrée
            if score:
                score = float(score)
                NoteDevoir.objects.update_or_create(
                    student=student,
                    subject_id=subject_id,
                    classe=classe,
                    sessionyear_id=sessionyear_id,
                    exam_id=devoir_id,
                    defaults={"score": score},
                )

        return JsonResponse({"success": True, "message": "Notes enregistrées avec succès."})

    # Si GET, récupérer les critères pour filtrer les données
    sessionyears = SessionYearModel.objects.all()
    devoirs = Devoir.objects.all()
    classes = Classe.objects.all()
    subjects = Subject.objects.all()

    context = {
        "sessionyears": sessionyears,
        "devoirs": devoirs,
        "classes": classes,
        "subjects": subjects,
    }
    return render(request, "notes/ajouter_notes.html", context)


def get_students(request, classe_id, devoir_id):
    # Récupérer la classe
    classe = get_object_or_404(Classe, id=classe_id)
    # Récupérer les étudiants de cette classe via student_class
    students = Student.objects.filter(student_class=classe)
    # Préparer les données des étudiants
    students_data = [{"id": student.id, "name": f"{student.first_name} {student.last_name}"} for student in students]
    return JsonResponse({"students": students_data})




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