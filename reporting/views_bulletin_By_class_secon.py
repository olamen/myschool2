from decimal import Decimal
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.db.models import Sum
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from .models import Student, Subject, NoteComposition, NoteDevoir, SessionYearModel

# Chemin du logo (modifie selon ton projet)
LOGO_PATH = "static/images/logo.png"

def generate_class_report_pdf(request, session_year_id, class_id):
    session_year = get_object_or_404(SessionYearModel, id=session_year_id)
    students = Student.objects.filter(student_class_id=class_id).order_by("first_name")

    # Calculer les moyennes générales et trier les étudiants
    students_with_avg = []
    
    for student in students:
        subjects = Subject.objects.filter(grade=student.student_class.grade, is_active=True)
        total_score = Decimal('0.0')
        total_coefficient = Decimal('0.0')

        for subject in subjects:
            comp1 = NoteComposition.objects.filter(student=student, subject=subject, sessionyear=session_year, composition__id=2).first()
            comp2 = NoteComposition.objects.filter(student=student, subject=subject, sessionyear=session_year, composition__id=3).first()
            comp3 = NoteComposition.objects.filter(student=student, subject=subject, sessionyear=session_year, composition__id=4).first()
            devoirs = NoteDevoir.objects.filter(student=student, subject=subject, sessionyear=session_year).aggregate(total=Sum('score'))['total'] or 0

            def get_valid_score(comp):
                return Decimal(comp.score) * comp.composition.coefficient if comp and comp.score else Decimal('0.0')

            total_coeff = sum([
                comp1.composition.coefficient if comp1 else 0,
                comp2.composition.coefficient if comp2 else 0,
                comp3.composition.coefficient if comp3 else 0,
                3  # Coefficient des devoirs
            ])
            
            moyenne = (get_valid_score(comp1) + get_valid_score(comp2) + get_valid_score(comp3) + Decimal(devoirs) * 3) / total_coeff if total_coeff else 0
            total_score += moyenne * subject.coefficient
            total_coefficient += subject.coefficient

        general_avg = total_score / total_coefficient if total_coefficient else 0
        students_with_avg.append((student, round(general_avg, 2)))

    # Trier les étudiants par moyenne décroissante
    students_with_avg.sort(key=lambda x: x[1], reverse=True)

    # Générer le fichier PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Bulletin_Annuel{student.student_class.name}_{session_year.name}.pdf"'
    pdf = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    for rank, (student, general_avg) in enumerate(students_with_avg, start=1):
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(200, height - 50, "École XYZ - Bulletin Annuel")

        pdf.setFont("Helvetica", 12)
        pdf.drawString(50, height - 80, f"Année Scolaire : {session_year.name}")
        pdf.drawString(50, height - 100, f"Nom de l'élève : {student.first_name} {student.last_name}")
        pdf.drawString(50, height - 120, f"Classe : {student.student_class.name}")
        pdf.drawString(50, height - 140, f"Rang : {rank}")  # Ajout du rang

        # Ajouter le logo
        try:
            pdf.drawInlineImage(LOGO_PATH, 400, height - 110, width=80, height=80)
        except Exception as e:
            print(f"Erreur lors du chargement du logo : {e}")

        y_position = height - 180
        pdf.setFont("Helvetica-Bold", 10)

        # Affichage du tableau des matières
        table_data = [["Matière", "Exam 1", "Exam 2", "Exam 3", "Devoirs", "Moyenne", "Coef", "Total"]]
        subjects = Subject.objects.filter(grade=student.student_class.grade, is_active=True)
        
        for subject in subjects:
            comp1 = NoteComposition.objects.filter(student=student, subject=subject, sessionyear=session_year, composition__id=2).first()
            comp2 = NoteComposition.objects.filter(student=student, subject=subject, sessionyear=session_year, composition__id=3).first()
            comp3 = NoteComposition.objects.filter(student=student, subject=subject, sessionyear=session_year, composition__id=4).first()
            devoirs = NoteDevoir.objects.filter(student=student, subject=subject, sessionyear=session_year).aggregate(total=Sum('score'))['total'] or 0

            moyenne = (get_valid_score(comp1) + get_valid_score(comp2) + get_valid_score(comp3) + Decimal(devoirs) * 3) / total_coeff if total_coeff else 0
            total = moyenne * subject.coefficient

            table_data.append([
                subject.name,
                comp1.score if comp1 else "-",
                comp2.score if comp2 else "-",
                comp3.score if comp3 else "-",
                devoirs,
                round(moyenne, 2),
                subject.coefficient,
                round(total, 2),
            ])

        # Afficher le tableau des matières
        table = Table(table_data, colWidths=[70, 50, 50, 50, 50, 50, 50, 50])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        table.wrapOn(pdf, width, height)
        table.drawOn(pdf, 50, y_position - len(subjects) * 20)

        # Affichage de la moyenne générale et la décision
        y_position -= (len(subjects) + 2) * 20
        pdf.drawString(50, y_position, "Moyenne Générale Annuelle :")
        pdf.drawString(250, y_position, str(general_avg))

        decision = "Très Bien" if general_avg >= 15 else "Bien" if general_avg >= 12 else "Passable" if general_avg >= 9 else "Redoublement"
        pdf.drawString(50, y_position - 20, f"Décision : {decision}")

        pdf.showPage()

    pdf.save()
    return response