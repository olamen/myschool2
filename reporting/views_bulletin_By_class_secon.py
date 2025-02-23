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

def generate_class_report_pdf(request, class_id, sessionyear_id):
    students = Student.objects.filter(student_class_id=class_id)
    session_year = get_object_or_404(SessionYearModel, id=sessionyear_id)

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    for student in students:
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(200, height - 50, "École XYZ - Bulletin Annuel")
        pdf.setFont("Helvetica", 12)
        pdf.drawString(50, height - 80, f"Année Scolaire : {session_year.name}")
        pdf.drawString(50, height - 100, f"Nom de l'élève : {student.first_name} {student.last_name}")
        pdf.drawString(50, height - 120, f"Classe : {student.student_class.name}")

        y_position = height - 160
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(50, y_position, "Matière")
        pdf.drawString(150, y_position, "Exam 1")
        pdf.drawString(220, y_position, "Exam 2")
        pdf.drawString(290, y_position, "Exam 3")
        pdf.drawString(360, y_position, "Devoirs")
        pdf.drawString(420, y_position, "Moyenne")
        pdf.drawString(490, y_position, "Coef")
        pdf.drawString(550, y_position, "Total")

        pdf.line(50, y_position - 5, 580, y_position - 5)

        subjects = Subject.objects.filter(grade=student.student_class.grade, is_active=True)
        total_yearly_score = Decimal('0.0')
        total_coefficient = Decimal('0.0')

        for subject in subjects:
            y_position -= 20
            if y_position < 50:
                pdf.showPage()
                y_position = height - 50

            comp1 = NoteComposition.objects.filter(student=student, subject=subject, sessionyear=session_year, composition__id=2).first()
            comp2 = NoteComposition.objects.filter(student=student, subject=subject, sessionyear=session_year, composition__id=3).first()
            comp3 = NoteComposition.objects.filter(student=student, subject=subject, sessionyear=session_year, composition__id=4).first()
            devoirs = NoteDevoir.objects.filter(student=student, subject=subject, sessionyear=session_year).aggregate(total=Sum('score'))['total'] or 0

            def get_valid_score(comp):
                if comp:
                    if comp.absence == 'ABJ':
                        return "ABJ"
                    return Decimal(comp.score) * comp.composition.coefficient if comp.score else Decimal('0.0')
                return Decimal('0.0')

            comp1_score = get_valid_score(comp1)
            comp2_score = get_valid_score(comp2)
            comp3_score = get_valid_score(comp3)
            devoirs_score = Decimal(str(devoirs)) * Decimal(3)

            valid_scores = [Decimal(score) for score in [comp1_score, comp2_score, comp3_score] if isinstance(score, Decimal)]
            total_coeff = sum([
                comp1.composition.coefficient if comp1 and isinstance(comp1_score, Decimal) else 0,
                comp2.composition.coefficient if comp2 and isinstance(comp2_score, Decimal) else 0,
                comp3.composition.coefficient if comp3 and isinstance(comp3_score, Decimal) else 0,
                3
            ])

            moyenne_finale = (sum(valid_scores) + devoirs_score) / total_coeff if total_coeff > 0 else "ABJ"
            note_finale = moyenne_finale * subject.coefficient if isinstance(moyenne_finale, Decimal) else moyenne_finale

            pdf.setFont("Helvetica", 10)
            pdf.drawString(50, y_position, subject.name)
            pdf.drawString(150, y_position, str(comp1_score) if isinstance(comp1_score, Decimal) else "ABJ")
            pdf.drawString(220, y_position, str(comp2_score) if isinstance(comp2_score, Decimal) else "ABJ")
            pdf.drawString(290, y_position, str(comp3_score) if isinstance(comp3_score, Decimal) else "ABJ")
            pdf.drawString(360, y_position, str(round(devoirs_score, 2)))
            pdf.drawString(420, y_position, str(round(moyenne_finale, 2)) if isinstance(moyenne_finale, Decimal) else "ABJ")
            pdf.drawString(490, y_position, str(subject.coefficient))
            pdf.drawString(550, y_position, str(round(note_finale, 2)) if isinstance(note_finale, Decimal) else "ABJ")

            if isinstance(note_finale, Decimal):
                total_yearly_score += note_finale
                total_coefficient += subject.coefficient

        yearly_average = round(total_yearly_score / total_coefficient, 2) if total_coefficient else 0

        y_position -= 30
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(50, y_position, "Moyenne Générale Annuelle :")
        pdf.drawString(200, y_position, str(yearly_average))

        y_position -= 20
        pdf.setFont("Helvetica-Bold", 10)
        decision = "Très Bien" if yearly_average >= 15 else "Bien" if yearly_average >= 12 else "Passable" if yearly_average >= 9 else "Redoublement"
        pdf.drawString(50, y_position, f"Décision : {decision}")

        y_position -= 40
        pdf.setFont("Helvetica", 10)
        pdf.drawString(50, y_position, "Signature de l'enseignant : __________________________")
        pdf.drawString(350, y_position, "Signature du Directeur : __________________________")

        pdf.showPage()

    pdf.save()
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="bulletins_classe.pdf"'
    return response
