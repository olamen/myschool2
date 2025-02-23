from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from decimal import Decimal
from django.db.models import Sum
from io import BytesIO
from students.models import Student, SessionYearModel, Subject
from notes.models import NoteComposition, NoteDevoir

# Chemin du logo de l'école
LOGO_PATH = "static/images/logo.png"  # Assurez-vous d'avoir le logo à cet emplacement

def generate_class_report_pdf(request, class_id, sessionyear_id):
    students = Student.objects.filter(student_class_id=class_id)
    session_year = get_object_or_404(SessionYearModel, id=sessionyear_id)
    
    student_scores = []
    for student in students:
        subjects = Subject.objects.filter(grade=student.student_class.grade, is_active=True)
        total_yearly_score = Decimal('0.0')
        total_coefficient = Decimal('0.0')
        
        for subject in subjects:
            comp1 = NoteComposition.objects.filter(student=student, subject=subject, sessionyear=session_year, composition__id=2).first()
            comp2 = NoteComposition.objects.filter(student=student, subject=subject, sessionyear=session_year, composition__id=3).first()
            comp3 = NoteComposition.objects.filter(student=student, subject=subject, sessionyear=session_year, composition__id=4).first()
            devoirs = NoteDevoir.objects.filter(student=student, subject=subject, sessionyear=session_year).aggregate(total=Sum('score'))['total'] or 0

            def get_valid_score(comp):
                if comp:
                    return Decimal(comp.score) * comp.composition.coefficient if comp.score else Decimal('0.0')
                return Decimal('0.0')

            comp1_score = get_valid_score(comp1)
            comp2_score = get_valid_score(comp2)
            comp3_score = get_valid_score(comp3)
            devoirs_score = Decimal(str(devoirs)) * Decimal(3)

            valid_scores = [Decimal(score) for score in [comp1_score, comp2_score, comp3_score] if isinstance(score, Decimal)]
            total_coeff = sum([
                comp1.composition.coefficient if comp1 else 0,
                comp2.composition.coefficient if comp2 else 0,
                comp3.composition.coefficient if comp3 else 0,
                3
            ])

            moyenne_finale = (sum(valid_scores) + devoirs_score) / total_coeff if total_coeff > 0 else Decimal('0.0')
            note_finale = moyenne_finale * subject.coefficient if isinstance(moyenne_finale, Decimal) else Decimal('0.0')

            if isinstance(note_finale, Decimal):
                total_yearly_score += note_finale
                total_coefficient += subject.coefficient
        
        yearly_average = round(total_yearly_score / total_coefficient, 2) if total_coefficient else Decimal('0.0')
        student_scores.append((student, yearly_average))
    
    # Trier les élèves par moyenne (de la plus grande à la plus petite)
    student_scores.sort(key=lambda x: x[1], reverse=True)
    
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    rank = 1
    for student, yearly_average in student_scores:
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(200, height - 50, "École XYZ - Bulletin Annuel")
        pdf.setFont("Helvetica", 12)
        pdf.drawString(50, height - 80, f"Année Scolaire : {session_year.name}")
        pdf.drawString(50, height - 100, f"Nom de l'élève : {student.first_name} {student.last_name}")
        pdf.drawString(50, height - 120, f"Classe : {student.student_class.name}")
        pdf.drawString(50, height - 140, f"Rang : {rank}")
        
        try:
            pdf.drawInlineImage(LOGO_PATH, width / 2 - 50, height - 70, width=100, height=100)
        except Exception as e:
            print(f"Erreur lors du chargement du logo : {e}")
        
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(width - 200, height - 50, "مدرسة XYZ")
        
        y_position = height - 160
        pdf.setFont("Helvetica-Bold", 10)
        pdf.setStrokeColor(colors.black)
        pdf.setFillColor(colors.lightgrey)
        pdf.rect(50, y_position - 10, 530, 20, fill=1)
        pdf.setFillColor(colors.black)
        headers = ["Matière", "Exam 1", "Exam 2", "Exam 3", "Devoirs", "Moyenne", "Coef", "Total"]
        x_positions = [50, 150, 220, 290, 360, 420, 490, 550]
        
        for i, header in enumerate(headers):
            pdf.drawString(x_positions[i], y_position, header)
        
        y_position -= 30
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(50, y_position, "Moyenne Générale Annuelle :")
        pdf.drawString(200, y_position, str(yearly_average))
        
        decision = "Très Bien" if yearly_average >= 15 else "Bien" if yearly_average >= 12 else "Passable" if yearly_average >= 9 else "Redoublement"
        pdf.drawString(50, y_position - 20, f"Décision : {decision}")
        
        pdf.showPage()
        rank += 1
    
    pdf.save()
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="bulletins_{student.student_class.name}_{session_year.name}.pdf"'
    return response

