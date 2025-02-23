from decimal import Decimal
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.db.models import Sum
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from students.models import Student, Subject, SessionYearModel
from notes.models import NoteComposition, NoteDevoir

LOGO_PATH = "static/images/logo.png"
DIRECTOR_SIGNATURE_PATH = "static/images/logo.png"

def get_valid_score(comp):
    if comp:
        if comp.absence == 'ABJ':
            return "ABJ"
        return Decimal(comp.score) * comp.composition.coefficient if comp.score else Decimal('0.0')
    return Decimal('0.0')

def generate_class_report_pdf(request, sessionyear_id, class_id):
    session_year = get_object_or_404(SessionYearModel, id=sessionyear_id)
    students = Student.objects.filter(student_class=class_id).order_by("first_name")
    subjects = Subject.objects.filter(grade=student.student_class.grade, is_active=True)  # Moved outside student loop

    students_with_avg = []
    
    for student in students:
        total_score = Decimal('0.0')
        total_coefficient = Decimal('0.0')
        total_yearly_score = Decimal('0.0')  # Added initialization

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
            total_valid_scores = sum(valid_scores)
            
            # Calculate coefficients
            total_coeff = sum([
                comp1.composition.coefficient if comp1 and isinstance(comp1_score, Decimal) else Decimal('0.0'),
                comp2.composition.coefficient if comp2 and isinstance(comp2_score, Decimal) else Decimal('0.0'),
                comp3.composition.coefficient if comp3 and isinstance(comp3_score, Decimal) else Decimal('0.0'),
                Decimal('3.0')
            ])

            # Calculate averages
            if total_coeff > 0:
                moyenne_finale = (total_valid_scores + devoirs_score) / total_coeff
                note_finale = moyenne_finale * subject.coefficient
            else:
                moyenne_finale = "ABJ"
                note_finale = "ABJ"

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

            # Handle display values
            comp1_display = str(round(comp1_score, 2)) if isinstance(comp1_score, Decimal) else "ABJ"
            comp2_display = str(round(comp2_score, 2)) if isinstance(comp2_score, Decimal) else "ABJ"
            comp3_display = str(round(comp3_score, 2)) if isinstance(comp3_score, Decimal) else "ABJ"
            devoirs_display = str(round(devoirs_score, 2))

            table_data.append([
                subject.name,
                comp1_display,
                comp2_display,
                comp3_display,
                devoirs_display,
                str(round(moyenne_finale, 2)) if isinstance(moyenne_finale, Decimal) else "ABJ",
                str(subject.coefficient),
                str(round(note_finale, 2)) if isinstance(note_finale, Decimal) else "ABJ",
                ""  # Appréciation
            ])

        # ... (rest of your PDF generation code)

    pdf.save()
    return response