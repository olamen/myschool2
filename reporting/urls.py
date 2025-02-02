from django.urls import path
from .views import exam_list, report_card_pdf,afficher_notes_devoir,afficher_notes_exam
from .views_print import print_notes,rep
from .views_excel import export_notes_to_excel
from .views_bulletin import *


urlpatterns = [ 
    path("exams/", exam_list, name="exam_list"),
    path("report_card/<int:student_id>/<int:exam_id>/", report_card_pdf, name="report_card_pdf"),
    path('notes_devoir/', afficher_notes_devoir, name='afficher_notes'),
    path('notes_exam/', afficher_notes_exam, name='afficher_notes_exams'),
    path('notes/export/', export_notes_to_excel, name='export_notes_to_excel'),
    path('notes/print/', print_notes, name='print_notes'),
    path('notes/rep/', rep, name='rep'),
    path('buletin_card/<int:student_id>/<int:trimestre_id>/<int:sessionyear_id>/', generate_report_card, name='generate_report_card'),
    path('class_report_cards/<int:classe_id>/<int:trimestre_id>/', generate_class_report_cards, name='generate_class_report_cards'),
    path('report_card/pdf/<int:student_id>/<int:trimestre_id>/', generate_pdf_report_card, name='generate_pdf_report_card'),

    path('reporting/final_report_card/<int:student_id>/<int:sessionyear_id>/', generate_final_report_card, name='final_report_card'),

]