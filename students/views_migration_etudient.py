from pyexpat.errors import messages

from django.shortcuts import render
from students.models import Classe, Student


def migrate_students(request):
    # Sélectionne les élèves du collège et du lycée
    students = Student.objects.filter(student_class__grade__name__in=['college', 'lycee'])

    migrated_students = []

    for student in students:
        # Calcul de la moyenne annuelle
        yearly_average = student.calculate_yearly_average()  # Assurez-vous que cette méthode existe dans votre modèle
        
        # Si la moyenne est supérieure à 9/20
        if yearly_average > 9:
            # Trouver la classe suivante
            current_class = student.student_class
            next_class = Classe.objects.filter(order=current_class.order + 1).first()
            
            # Si une classe suivante existe, on migre l'élève
            if next_class:
                student.student_class = next_class
                student.save()
                migrated_students.append(student)
    
    # Message de succès
    messages.success(request, f"{len(migrated_students)} élèves ont été migrés avec succès !")

    context = {
        "migrated_students": migrated_students
    }
    return render(request, 'reporting/migrate_students.html', context)