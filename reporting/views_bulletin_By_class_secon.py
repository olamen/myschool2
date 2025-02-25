from decimal import Decimal
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.db.models import Sum
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from students.models import Student, Subject, SessionYearModel
from notes.models import NoteComposition, NoteDevoir

LOGO_PATH = "static/images/logo.png"

def generate_class_report_pdf(request, sessionyear_id, class_id):
    session_year = get_object_or_404(SessionYearModel, id=sessionyear_id)
    students = Student.objects.filter(student_class_id=class_id).order_by("first_name")

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

            total_coeff = sum([
                comp1.composition.coefficient if comp1 else 0,
                comp2.composition.coefficient if comp2 else 0,
                comp3.composition.coefficient if comp3 else 0,
                3  # Coefficient des devoirs
            ])

            scores = [get_valid_score(comp1), get_valid_score(comp2), get_valid_score(comp3)]
            valid_scores = [score for score in scores if score is not None and isinstance(score, Decimal)]

            moyenne = (sum(valid_scores) + Decimal(devoirs) * 3) / total_coeff if total_coeff else 0

            if isinstance(moyenne, Decimal):
                total_score += moyenne * subject.coefficient
                total_coefficient += subject.coefficient

        general_avg = total_score / total_coefficient if total_coefficient else 0
        students_with_avg.append((student, round(general_avg, 2)))

    students_with_avg.sort(key=lambda x: x[1], reverse=True)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Bulletin_Annuel_{session_year.name}.pdf"'
    pdf = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    for rank, (student, general_avg) in enumerate(students_with_avg, start=1):
        # ... (votre code d'en-tête PDF et d'informations sur l'étudiant) ...

        y_position = height - 180
        pdf.setFont("Helvetica-Bold", 10)

        table_data = [["Matière", "Exam 1", "Exam 2", "Exam 3", "Devoirs", "Moyenne", "Coef", "Total"]]
        subjects = Subject.objects.filter(grade=student.student_class.grade, is_active=True)

        for subject in subjects:
            comp1 = NoteComposition.objects.filter(student=student, subject=subject, sessionyear=session_year, composition__id=2).first()
            comp2 = NoteComposition.objects.filter(student=student, subject=subject, sessionyear=session_year, composition__id=3).first()
            comp3 = NoteComposition.objects.filter(student=student, subject=subject, sessionyear=session_year, composition__id=4).first()
            devoirs = NoteDevoir.objects.filter(student=student, subject=subject, sessionyear=session_year).aggregate(total=Sum('score'))['total'] or 0

            scores = [get_valid_score(comp1), get_valid_score(comp2), get_valid_score(comp3)]
            valid_scores = [score for score in scores if score is not None and isinstance(score, Decimal)]

            moyenne = (sum(valid_scores) + Decimal(devoirs) * 3) / total_coeff if total_coeff else 0
            total = moyenne * subject.coefficient if isinstance(moyenne, Decimal) else moyenne

            # Afficher l'absence ou le score
            comp1_display = comp1.absence if comp1 and comp1.absence else comp1.score if comp1 and comp1.score is not None else "-"
            comp2_display = comp2.absence if comp2 and comp2.absence else comp2.score if comp2 and comp2.score is not None else "-"
            comp3_display = comp3.absence if comp3 and comp3.absence else comp3.score if comp3 and comp3.score is not None else "-"

            table_data.append([
                subject.name,
                comp1_display,
                comp2_display,
                comp3_display,
                devoirs,
                round(moyenne, 2) if isinstance(moyenne,Decimal) else moyenne,
                subject.coefficient,
                round(total, 2) if isinstance(total,Decimal) else total,
            ])

        # ... (votre code de style de tableau et de dessin existant) ...

        y_position -= (len(subjects) + 2) * 20
        pdf.drawString(50, y_position, "Moyenne Générale Annuelle :")
        pdf.drawString(250, y_position, str(general_avg))

        decision = "Très Bien" if general_avg >= 15 else "Bien" if general_avg >= 12 else "Passable" if general_avg >= 9 else "Redoublement"
        pdf.drawString(50, y_position - 20, f"Décision : {decision}")

        pdf.showPage()

    pdf.save()
    return response