# tasks.py
from celery import shared_task
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django.db.models import Sum
from decimal import Decimal
from students.models import Student, SessionYearModel, Subject, Classe
from notes.models import NoteComposition, NoteDevoir

from weasyprint import HTML
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
# tasks.py
from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task
def test_celery_connection():
    logger.info("Celery connection test successful!")
    return "Celery test successful"

@shared_task
def generate_class_report_cards_task(class_id, sessionyear_id, user_email):
    """Generates class report cards and sends a download link via email."""
    student_class = get_object_or_404(Classe, id=class_id)
    session_year = get_object_or_404(SessionYearModel, id=sessionyear_id)
    students = Student.objects.filter(student_class=student_class)

    pdf_parts = []

    for student in students:
        if student.student_class.grade.name.lower() == "primaire":
            continue

        subjects = Subject.objects.filter(grade=student.student_class.grade, is_active=True)
        results = []
        total_yearly_score = Decimal('0.0')
        total_coefficient = Decimal('0.0')

        # ... (Your existing report card generation logic here) ...
        for subject in subjects:
            comp1 = NoteComposition.objects.filter(student=student, subject=subject, sessionyear=session_year, composition__id=2).first()
            comp2 = NoteComposition.objects.filter(student=student, subject=subject, sessionyear=session_year, composition__id=3).first()
            comp3 = NoteComposition.objects.filter(student=student, subject=subject, sessionyear=session_year, composition__id=4).first()

            devoirs = NoteDevoir.objects.filter(student=student, subject=subject, sessionyear=session_year).aggregate(
                total=Sum('score')
            )['total'] or 0

            def get_valid_score(comp):
                if comp:
                    if comp.absence == 'ABJ':
                        return "ABJ"
                    elif comp.score is not None:
                        return Decimal(comp.score) * comp.composition.coefficient
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

            if total_coeff > 0:
                moyenne_finale = (sum(valid_scores) + devoirs_score) / total_coeff
            else:
                moyenne_finale = "ABJ"

            note_finale = moyenne_finale * subject.coefficient if isinstance(moyenne_finale, Decimal) else moyenne_finale

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

        yearly_average = round(total_yearly_score / total_coefficient, 2) if total_coefficient else 0

        context = {
            "student": student,
            "session_year": session_year,
            "results": results,
            "yearly_average": yearly_average
        }

        template = get_template("reporting/final_report_card.html")
        html_content = template.render(context)
        pdf_parts.append(html_content)

    combined_html = "".join(pdf_parts)
    pdf_file = HTML(string=combined_html, base_url=settings.STATIC_ROOT).write_pdf()

    filename = f"report_cards_{student_class.name}_{session_year.name}.pdf"
    file_path = default_storage.save(f"reports/{filename}", ContentFile(pdf_file))
    file_url = default_storage.url(file_path)

    # Send email with download link
    subject = "Your Report Cards are Ready"
    message = f"Your class report cards are ready for download: {file_url}"
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email])

    return file_url