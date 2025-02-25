from decimal import Decimal
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.db.models import Sum
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from students.models import Student, Subject, SessionYearModel
from notes.models import NoteComposition, NoteDevoir

LOGO_PATH = "static/images/logo.png"
DIRECTOR_SIGNATURE_PATH = "static/images/logo.png"

def get_valid_score(comp):
    if comp:
        if comp.absence == 'ABJ':
            return None  # Return None for justified absence
        if comp.score is not None:
            return Decimal(comp.score) * comp.composition.coefficient
        return Decimal('0.0')
    return Decimal('0.0')

def generate_class_report_pdf(request, sessionyear_id, class_id):
    session_year = get_object_or_404(SessionYearModel, id=sessionyear_id)
    students = Student.objects.filter(student_class=class_id).order_by("first_name")
    students_with_avg = []

    for student in students:
        subjects = Subject.objects.filter(grade=student.student_class.grade, is_active=True)
        total_yearly_score = Decimal('0.0')
        total_coefficient = Decimal('0.0')

        for subject in subjects:
            comp1 = NoteComposition.objects.filter(student=student, subject=subject, sessionyear=session_year, composition__id=2).first()
            comp2 = NoteComposition.objects.filter(student=student, subject=subject, sessionyear=session_year, composition__id=3).first()
            comp3 = NoteComposition.objects.filter(student=student, subject=subject, sessionyear=session_year, composition__id=4).first()
            devoirs = NoteDevoir.objects.filter(student=student, subject=subject, sessionyear=session_year).aggregate(total=Sum('score'))['total'] or 0

            comp1_score = get_valid_score(comp1)
            comp2_score = get_valid_score(comp2)
            comp3_score = get_valid_score(comp3)
            devoirs_score = Decimal(str(devoirs)) * Decimal(3)

            # Handle valid scores
            valid_scores = [score for score in [comp1_score, comp2_score, comp3_score] if isinstance(score, Decimal)]
            total_valid_scores = sum(valid_scores) if valid_scores else Decimal('0.0')

            # Calculate coefficients
            total_coeff = sum([
                comp1.composition.coefficient if comp1 and isinstance(comp1_score, Decimal) else Decimal('0.0'),
                comp2.composition.coefficient if comp2 and isinstance(comp2_score, Decimal) else Decimal('0.0'),
                comp3.composition.coefficient if comp3 and isinstance(comp3_score, Decimal) else Decimal('0.0'),
                Decimal('3.0')
            ])

            # Calculate averages
            if total_coeff > 0 and valid_scores is not None:
                moyenne_finale = (total_valid_scores + devoirs_score) / total_coeff
                note_finale = moyenne_finale * subject.coefficient
            else:
                moyenne_finale = "ABJ" if any(comp and comp.absence == 'ABJ' for comp in [comp1, comp2, comp3]) else "ABS"
                note_finale = "ABJ" if any(comp and comp.absence == 'ABJ' for comp in [comp1, comp2, comp3]) else "ABS"

            # Update totals
            if isinstance(note_finale, Decimal):
                total_yearly_score += note_finale
                total_coefficient += subject.coefficient

        # Calculate yearly average
        yearly_average = round(total_yearly_score / total_coefficient, 2) if total_coefficient else Decimal('0.0')
        students_with_avg.append((student, yearly_average))

    # Sort students by average
    students_with_avg.sort(key=lambda x: x[1], reverse=True)

    # PDF Generation
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Bulletin_Annuel_Classe_{class_id}_{session_year.name}.pdf"'
    pdf = canvas.Canvas(response, pagesize=landscape(A4))
    width, height = landscape(A4)

    for rank, (student, general_avg) in enumerate(students_with_avg, start=1):
        # PDF content creation
        # ... (keep your existing PDF layout code)

        # Revised table data population
        table_data = [["Matière", "Exam 1", "Exam 2", "Exam 3", "Devoirs", "Moyenne", "Coef", "Total", "Appréciation"]]

        for subject in subjects:
            comp1 = NoteComposition.objects.filter(student=student, subject=subject, sessionyear=session_year, composition__id=2).first()
            comp2 = NoteComposition.objects.filter(student=student, subject=subject, sessionyear=session_year, composition__id=3).first()
            comp3 = NoteComposition.objects.filter(student=student, subject=subject, sessionyear=session_year, composition__id=4).first()
            devoirs = NoteDevoir.objects.filter(student=student, subject=subject, sessionyear=session_year).aggregate(total=Sum('score'))['total'] or 0

            # Get scores using the helper function
            comp1_score = get_valid_score(comp1)
            comp2_score = get_valid_score(comp2)
            comp3_score = get_valid_score(comp3)
            devoirs_score = Decimal(str(devoirs)) * Decimal(3)

            # Handle display values and absence status
            comp1_display = comp1.absence if comp1 and comp1.absence else str(round(comp1_score, 2)) if isinstance(comp1_score, Decimal) else "0.00"
            comp2_display = comp2.absence if comp2 and comp2.absence else str(round(comp2_score, 2)) if isinstance(comp2_score, Decimal) else "0.00"
            comp3_display = comp3.absence if comp3 and comp3.absence else str(round(comp3_score, 2)) if isinstance(comp3_score, Decimal) else "0.00"
            devoirs_display = str(round(devoirs_score, 2))

            moyenne_display = moyenne_finale if isinstance(moyenne_finale, str) else str(round(moyenne_finale, 2))
            note_display = note_finale if isinstance(note_finale, str) else str(round(note_finale, 2))

            table_data.append([
                subject.name,
                comp1_display,
                comp2_display,
                comp3_display,
                devoirs_display,
                moyenne_display,
                str(subject.coefficient),
                note_display,
                ""  # Appréciation
            ])

        # ... (rest of your PDF generation code)

    pdf.save()
    return response