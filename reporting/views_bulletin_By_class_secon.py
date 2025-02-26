from decimal import Decimal
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.db.models import Sum
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from students.models import Student, Subject, SessionYearModel
from notes.models import NoteComposition, NoteDevoir

LOGO_PATH = "static/images/logo.png"

def generate_class_report_pdf(request, sessionyear_id, class_id):
    session_year = get_object_or_404(SessionYearModel, id=sessionyear_id)
    students = Student.objects.filter(student_class_id=class_id).order_by("first_name")

    students_with_avg = []

    def get_valid_score(comp):
        if comp:
            if comp.absence == 'ABJ':
                return None  # Retourne None pour exclusion du calcul
            elif comp.absence == 'ABS':
                return "ABS"
            elif comp.score is not None:
                return Decimal(comp.score) * comp.composition.coefficient
            else:
                return Decimal('0.0')
        return Decimal('0.0')

    for student in students:
        subjects = Subject.objects.filter(grade=student.student_class.grade, is_active=True)
        total_score = Decimal('0.0')
        total_coefficient = Decimal('0.0')

        for subject in subjects:
            comp1 = NoteComposition.objects.filter(student=student, subject=subject, sessionyear=session_year, composition__id=2).first()
            comp2 = NoteComposition.objects.filter(student=student, subject=subject, sessionyear=session_year, composition__id=3).first()
            comp3 = NoteComposition.objects.filter(student=student, subject=subject, sessionyear=session_year, composition__id=4).first()
            devoirs = NoteDevoir.objects.filter(student=student, subject=subject, sessionyear=session_year).aggregate(total=Sum('score'))['total'] or 0

            scores = [get_valid_score(comp1), get_valid_score(comp2), get_valid_score(comp3)]
            valid_scores = [score for score in scores if score is not None and isinstance(score, Decimal)]
            valid_coeffs = sum([comp.composition.coefficient for comp in [comp1, comp2, comp3] if comp and comp.absence != 'ABJ'])

            total_coeff = valid_coeffs + 3  # Coefficient des devoirs

            moyenne = (sum(valid_scores) + Decimal(devoirs) * 3) / total_coeff if total_coeff else 0

            if isinstance(moyenne, Decimal):
                total_score += moyenne * subject.coefficient
                total_coefficient += subject.coefficient

        general_avg = total_score / total_coefficient if total_coefficient else 0
        students_with_avg.append((student, round(general_avg, 2)))

    students_with_avg.sort(key=lambda x: x[1], reverse=True)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Bulletin_Annuel_{session_year.name}.pdf"'
    pdf = canvas.Canvas(response, pagesize=landscape(A4))
    width, height = landscape(A4)

    # Left side: Logo
    pdf.drawImage(LOGO_PATH, 50, height - 100, width=100, height=100)  

    # Center: School Name and Year
    pdf.drawString(200, height - 70, "École XYZ - Bulletin Annuel")
    pdf.drawString(200, height - 90, f"Année Scolaire : {session_year.name}")

    # Right side: Custom text (Top Right)
    pdf.setFont("Helvetica", 14)
    pdf.drawString(width - 200, height - 70, "Date : 20/02/2025")
    pdf.drawString(width - 200, height - 90, "N° Ref: 123456")

    for rank, (student, general_avg) in enumerate(students_with_avg, start=1):
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(50, height - 140, f"Nom de l'élève : {student.first_name} {student.last_name}")
        pdf.drawString(50, height - 160, f"Classe : {student.student_class.name}")
        pdf.drawString(50, height - 180, f"Rang : {rank}")

        y_position = height - 180

        table_data = [["Matière", "Exam 1", "Exam 2", "Exam 3", "Devoirs", "Moyenne", "Coef", "Total","Appréciation"]]
        subjects = Subject.objects.filter(grade=student.student_class.grade, is_active=True)

        for subject in subjects:
            comp1 = NoteComposition.objects.filter(student=student, subject=subject, sessionyear=session_year, composition__id=2).first()
            comp2 = NoteComposition.objects.filter(student=student, subject=subject, sessionyear=session_year, composition__id=3).first()
            comp3 = NoteComposition.objects.filter(student=student, subject=subject, sessionyear=session_year, composition__id=4).first()
            devoirs = NoteDevoir.objects.filter(student=student, subject=subject, sessionyear=session_year).aggregate(total=Sum('score'))['total'] or 0

            scores = [get_valid_score(comp1), get_valid_score(comp2), get_valid_score(comp3)]
            valid_scores = [score for score in scores if score is not None and isinstance(score, Decimal)]
            valid_coeffs = sum([comp.composition.coefficient for comp in [comp1, comp2, comp3] if comp and comp.absence != 'ABJ'])

            total_coeff = valid_coeffs + 3  # Coefficient des devoirs

            moyenne = (sum(valid_scores) + Decimal(devoirs) * 3) / total_coeff if total_coeff else 0
            total = moyenne * subject.coefficient if isinstance(moyenne, Decimal) else moyenne

            comp1_display = comp1.absence if comp1 and comp1.absence else comp1.score if comp1 and comp1.score is not None else "-"
            comp2_display = comp2.absence if comp2 and comp2.absence else comp2.score * comp2.composition.coefficient if comp2 and comp2.score is not None else "-"
            comp3_display = comp3.absence if comp3 and comp3.absence else comp3.score * comp3.composition.coefficient if comp3 and comp3.score is not None else "-"

            table_data.append([
                subject.name,
                comp1_display,
                comp2_display,
                comp3_display,
                devoirs * 3,
                round(moyenne, 2) if isinstance(moyenne, Decimal) else moyenne,
                subject.coefficient,
                round(total, 2) if isinstance(total, Decimal) else total,
            ])
        page_width = landscape(A4)[0] - 80
        col_widths = [
                page_width * 0.20,  # Matière (20%)
                page_width * 0.08,  # Exam 1 (8%)
                page_width * 0.08,  # Exam 2 (8%)
                page_width * 0.08,  # Exam 3 (8%)
                page_width * 0.08,  # Devoirs (8%)
                page_width * 0.10,  # Moyenne (10%)
                page_width * 0.06,  # Coefficient (6%)
                page_width * 0.08,  # Total (8%)
                page_width * 0.13,  # Appreciation (13%)
            ]
        table = Table(table_data , colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),  # En-tête en 12 pt
            ('FONTSIZE', (0, 1), (-1, -1), 12),  # Contenu en 10 pt
            ('BOTTOMPADDING', (0, 0), (-1, 0), 15),
            ('TOPPADDING', (0, 0), (-1, 0), 15),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        table.wrapOn(pdf, width, height)
        table.drawOn(pdf, 50, y_position - 20 * len(subjects) - 40)

        # Adjust the y_position to create space between the table and the next text
        y_position -= (len(subjects) + 2) * 20 + 20  # Add extra space
        pdf.drawString(50, y_position, "Moyenne Générale Annuelle :")
        pdf.drawString(350, y_position, str(general_avg))

        decision = "Très Bien" if general_avg >= 15 else "Bien" if general_avg >= 12 else "Passable" if general_avg >= 9 else "Redoublement"
        pdf.drawString(50, y_position - 20, f"Décision : {decision}")

        pdf.showPage()

    pdf.save()
    return response
