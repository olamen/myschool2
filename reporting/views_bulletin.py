from django.db.models import Sum, F, Case, When, FloatField
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from notes.models import NoteComposition, NoteDevoir
from students.models import Student, Subject, Trimestre, SessionYearModel
from weasyprint import HTML
from django.template.loader import render_to_string
from itertools import chain
from decimal import Decimal



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


@login_required
def generate_final_report_card(request, student_id, sessionyear_id):
    student = get_object_or_404(Student, id=student_id)
    session_year = get_object_or_404(SessionYearModel, id=sessionyear_id)

    print("DEBUG: Étudiant -", student)
    print("DEBUG: Année scolaire -", session_year)

    # Vérification si c'est un élève du secondaire ou du lycée
    if student.student_class.grade.name.lower() == "primaire":
        return render(request, 'reporting/not_allowed.html', {"message": "Les élèves du primaire ne sont pas concernés."})

    subjects = Subject.objects.filter(grade=student.student_class.grade)
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

        # Calcul des notes pondérées avec les coefficients
        comp1_score = (Decimal(comp1.score) * Decimal(1)) if comp1 else Decimal('0.0')
        comp2_score = (Decimal(comp2.score) * Decimal(2)) if comp2 else Decimal('0.0')
        comp3_score = (Decimal(comp3.score) * Decimal(3)) if comp3 else Decimal('0.0')

        print("DEBUG: Comp1 Score -", comp1_score)
        print("DEBUG: Comp2 Score -", comp2_score)
        print("DEBUG: Comp3 Score -", comp3_score)

        devoirs_score = Decimal(str(devoirs)) * Decimal(3)
        print("DEBUG: Devoirs Score -", devoirs_score)

        # Somme des coefficients fixes
        total_coeff = Decimal(1 + 2 + 3 + 3)
        print("DEBUG: Total Coefficient Fixe -", total_coeff)

        # Calcul de la moyenne finale de la matière
        moyenne_finale = (comp1_score + comp2_score + comp3_score + devoirs_score) / total_coeff
        print("DEBUG: Moyenne Finale -", moyenne_finale)

        # Calcul de la note finale avec le coefficient de la matière
        note_finale = moyenne_finale * subject.coefficient
        print("DEBUG: Note Finale -", note_finale)
        
        results.append({
            "subject": subject.name,
            "comp1": round(comp1_score, 2),
            "comp2": round(comp2_score, 2),
            "comp3": round(comp3_score, 2),
            "devoirs": round(devoirs_score, 2),
            "moyenne_finale": round(moyenne_finale, 2),
            "note_finale": round(note_finale, 2),
            "coefficient": subject.coefficient
        })

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