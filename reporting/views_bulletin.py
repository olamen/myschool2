import io
from django.db.models import Sum, F, FloatField
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from notes.models import NoteComposition, NoteDevoir
from students.models import Classe, Student, Subject, Trimestre, SessionYearModel
from weasyprint import HTML
from django.template.loader import render_to_string
from decimal import Decimal
from django.template.loader import get_template
from xhtml2pdf import pisa



def calculate_cumulative_scores(student, trimestre):
    """
    Calcule le score cumulé (devoir + composition) pour un étudiant sur un trimestre.
    """
    # Somme pondérée des devoirs
    devoirs = NoteDevoir.objects.filter(student=student, trimestre=trimestre).aggregate(
        total=Sum(F('score') * F('coefficient'), output_field=FloatField())
    )['total'] or 0

    # Score pondéré de la composition
    composition = NoteComposition.objects.filter(student=student, trimestre=trimestre).first()
    composition_score = (composition.score * composition.coefficient) if composition else 0

    return devoirs + composition_score

def calculate_yearly_cumulative(student, trimestre):
    """
    Calcule le score cumulé annuel jusqu'à un trimestre donné.
    """
    return sum(calculate_cumulative_scores(student, t) for t in Trimestre.objects.filter(id__lte=trimestre.id))

@login_required
def generate_report_card(request, student_id, trimestre_id, sessionyear_id):
    student = get_object_or_404(Student, id=student_id)
    trimestre = get_object_or_404(Trimestre, id=trimestre_id)
    session_year = get_object_or_404(SessionYearModel, id=sessionyear_id)
    student_grade = student.student_class.grade.name.lower()

    subjects = Subject.objects.filter(grade=student.student_class.grade)
    results = []

    total_trimester_score = 0
    total_trimester_coefficient = 0

    for subject in subjects:
        # Calcul des notes de devoir et composition
        devoirs = NoteDevoir.objects.filter(student=student, subject=subject, trimestre=trimestre).aggregate(
            total=Sum(F('score') * F('coefficient'), output_field=FloatField())
        )['total'] or 0

        composition = NoteComposition.objects.filter(student=student, subject=subject, trimestre=trimestre).first()
        composition_score = (composition.score * composition.coefficient) if composition else 0

        # Score total du trimestre pour la matière
        total_score = devoirs + composition_score
        coefficient = subject.coefficient if subject.coefficient else 1

        total_trimester_score += total_score
        total_trimester_coefficient += coefficient

        results.append({
            "subject": subject.name,
            "devoirs": round(devoirs, 2),
            "composition": round(composition_score, 2),
            "total": round(total_score, 2),
            "coefficient": coefficient,
            "normalized_score": round((total_score / coefficient) * 20 if coefficient else 0, 2),
        })

    trimester_score = round((total_trimester_score / total_trimester_coefficient) * 20 if total_trimester_coefficient else 0, 2)
    yearly_score = round((calculate_yearly_cumulative(student, trimestre) / total_trimester_coefficient) * 20 if total_trimester_coefficient else 0, 2)

    context = {
        "student": student,
        "trimestre": trimestre,
        "session_year": session_year,
        "results": results,
        "trimester_score": trimester_score,
        "yearly_score": yearly_score,
    }

    return render(request, "reporting/report_card.html", context)

#Bulletin pour les élèves du secondaire et lycee
@login_required
def generate_final_report_card(request, student_id, sessionyear_id):
    student = get_object_or_404(Student, id=student_id)
    session_year = get_object_or_404(SessionYearModel, id=sessionyear_id)

    print("DEBUG: Étudiant -", student)
    print("DEBUG: Année scolaire -", session_year)

    # Vérification si c'est un élève du secondaire ou du lycée
    if student.student_class.grade.name.lower() == "primaire":
        return redirect('report_card_primaire', student_id=student.id, sessionyear_id=session_year.id)

    subjects = Subject.objects.filter(grade=student.student_class.grade, is_active=True)
    print("DEBUG: Matières trouvées -", subjects)

    results = []
    total_yearly_score = Decimal('0.0')
    total_coefficient = Decimal('0.0')

    for subject in subjects:
        print("\nDEBUG: Matière en cours -", subject.name)

        # Récupération des compositions
        comp1 = NoteComposition.objects.filter(student=student, subject=subject, sessionyear=session_year, composition__id=2).first()
        comp2 = NoteComposition.objects.filter(student=student, subject=subject, sessionyear=session_year, composition__id=3).first()
        comp3 = NoteComposition.objects.filter(student=student, subject=subject, sessionyear=session_year, composition__id=4).first()

        print("DEBUG: Comp1 -", comp1)
        print("DEBUG: Comp2 -", comp2)
        print("DEBUG: Comp3 -", comp3)

        # Calcul des devoirs pour l'année
        devoirs = NoteDevoir.objects.filter(student=student, subject=subject, sessionyear=session_year).aggregate(
            total=Sum('score')
        )['total'] or 0
        print("DEBUG: Total Devoirs -", devoirs)

        def get_valid_score(comp):
            """Retourne le score pondéré ou 'ABJ' si absence justifiée"""
            if comp:
                if comp.absence == 'ABJ':
                    return "ABJ"
                elif comp.score is not None:
                    return Decimal(comp.score) * comp.composition.coefficient
            return Decimal('0.0')  # Score ignoré si absence justifiée

        # Correction ici (assure que la fonction est bien utilisée)
        comp1_score = get_valid_score(comp1)
        comp2_score = get_valid_score(comp2)
        comp3_score = get_valid_score(comp3)

        devoirs_score = Decimal(str(devoirs)) * Decimal(3)
        print("DEBUG: Devoirs Score -", devoirs_score)

        # Convertir uniquement les valeurs numériques, ignorer les "ABJ"
        valid_scores = [Decimal(score) for score in [comp1_score, comp2_score, comp3_score] if isinstance(score, Decimal)]

        # Recalculer total_coeff en ignorant les absences
        total_coeff = sum([
            comp1.composition.coefficient if comp1 and isinstance(comp1_score, Decimal) else 0,
            comp2.composition.coefficient if comp2 and isinstance(comp2_score, Decimal) else 0,
            comp3.composition.coefficient if comp3 and isinstance(comp3_score, Decimal) else 0,
            3  # Devoirs toujours pris en compte
        ])

        # Éviter la division par zéro
        if total_coeff > 0:
            moyenne_finale = (sum(valid_scores) + devoirs_score) / total_coeff
        else:
            moyenne_finale = "ABJ"

        # Calcul de la note finale avec le coefficient de la matière
        note_finale = moyenne_finale * subject.coefficient if isinstance(moyenne_finale, Decimal) else moyenne_finale
        print("DEBUG: Note Finale -", note_finale)

        results.append({
            "subject": subject.name,
            "comp1": round(comp1_score, 2) if isinstance(comp1_score, Decimal) else comp1_score,
            "comp2": round(comp2_score, 2) if isinstance(comp2_score, Decimal) else comp2_score,
            "comp3": round(comp3_score, 2) if isinstance(comp3_score, Decimal) else comp3_score,
            "devoirs": round(devoirs_score, 2),
            "moyenne_finale": round(moyenne_finale, 2) if isinstance(moyenne_finale, Decimal) else moyenne_finale,
            "note_finale": round(note_finale, 2) if isinstance(note_finale, Decimal) else note_finale,
            "coefficient": subject.coefficient
        })

        if isinstance(note_finale, Decimal):
            total_yearly_score += note_finale
            total_coefficient += subject.coefficient

    print("DEBUG: Total Yearly Score -", total_yearly_score)
    print("DEBUG: Total Coefficient -", total_coefficient)

    yearly_average = round(total_yearly_score / total_coefficient, 2) if total_coefficient else 0
    print("DEBUG: Yearly Average -", yearly_average)

    context = {
        "student": student,
        "session_year": session_year,
        "results": results,
        "yearly_average": yearly_average
    }

    return render(request, "reporting/final_report_card.html", context)

@login_required
def select_class_for_report(request):
    session_years = SessionYearModel.objects.all()
    classes = Classe.objects.all()
    
    context = {
        'session_years': session_years,
        'classes': classes
    }
    
    return render(request, 'reporting/bulletinbyclass.html', context)

@login_required
def generate_class_report_cards(request, sessionyear_id, class_id):
    session_year = SessionYearModel.objects.get(id=sessionyear_id)
    students = Student.objects.filter(student_class_id=class_id).order_by('-id')  # Tri par moyenne décroissante
    
    template = get_template('reporting/final_report_card.html')
    context = {'students': students, 'session_year': session_year}
    
    html = template.render(context)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)
    
    if not pdf.err:
        return FileResponse(result, content_type='application/pdf')
    return None 


#bulletin pour les élèves du primaire
@login_required
def generate_report_card_primaire(request, student_id, sessionyear_id):
    student = get_object_or_404(Student, id=student_id)
    session_year = get_object_or_404(SessionYearModel, id=sessionyear_id)

    # Vérifiez si l'élève est en primaire
    if student.student_class.grade.name.lower() != "primaire":
        return redirect('final_report_card', student_id=student.id, sessionyear_id=session_year.id)

    # Récupération des matières pour le primaire
    subjects = Subject.objects.filter(grade=student.student_class.grade, is_active=True)

    results = []
    total_points = Decimal('0.0')
    total_max_points = Decimal('0.0')

    for subject in subjects:
        # Récupération des notes pour chaque composition
        comp1 = NoteComposition.objects.filter(student=student, subject=subject, sessionyear=session_year, composition__id=2).first()
        comp2 = NoteComposition.objects.filter(student=student, subject=subject, sessionyear=session_year, composition__id=3).first()
        comp3 = NoteComposition.objects.filter(student=student, subject=subject, sessionyear=session_year, composition__id=4).first()

        # Calcul des devoirs pour l'année
        devoirs = NoteDevoir.objects.filter(student=student, subject=subject, sessionyear=session_year).aggregate(
            total=Sum('score')
        )['total'] or 0

        # Calcul des scores
        comp1_score = Decimal(comp1.score) if comp1 else Decimal('0.0')
        comp2_score = Decimal(comp2.score) if comp2 else Decimal('0.0')
        comp3_score = Decimal(comp3.score) if comp3 else Decimal('0.0')
        devoirs_score = Decimal(str(devoirs))

        # Somme des points obtenus
        total_score = comp1_score + comp2_score + comp3_score + devoirs_score

        # Calcul du pourcentage (optionnel)
        max_points = subject.points or 0  # Utilisation des points du modèle Subject
        percentage = (total_score / max_points) * 100 if max_points > 0 else 0

        results.append({
            "subject": subject.name,
            "comp1": comp1_score,
            "comp2": comp2_score,
            "comp3": comp3_score,
            "devoirs": devoirs_score,
            "total_score": total_score,
            "max_points": max_points,
            "percentage": round(percentage, 2)
        })

        total_points += total_score
        total_max_points += max_points

    # Calcul de la moyenne générale en pourcentage
    yearly_average = (total_points / total_max_points) * 100 if total_max_points > 0 else 0

    context = {
        "student": student,
        "session_year": session_year,
        "results": results,
        "yearly_average": round(yearly_average, 2)
    }

    return render(request, "reporting/final_report_card_primaire.html", context)


@login_required
def generate_pdf_report_card(request, student_id, trimestre_id):
    student = get_object_or_404(Student, id=student_id)
    trimestre = get_object_or_404(Trimestre, id=trimestre_id)

    trimester_score = round(calculate_cumulative_scores(student, trimestre), 2)
    yearly_score = round(calculate_yearly_cumulative(student, trimestre), 2)

    html_string = render_to_string('reporting/report_card.html', {
        'student': student,
        'trimestre': trimestre,
        'trimester_score': trimester_score,
        'yearly_score': yearly_score,
    })

    pdf = HTML(string=html_string).write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="bulletin_{student.last_name}.pdf"'
    return response