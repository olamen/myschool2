from django.urls import path
from .views import exam_list, report_card_pdf,afficher_notes_devoir,afficher_notes_exam
from .views_print import print_notes
from .views_excel import export_notes_to_excel


urlpatterns = [ 
    path("exams/", exam_list, name="exam_list"),
    path("report_card/<int:student_id>/<int:exam_id>/", report_card_pdf, name="report_card_pdf"),
    path('notes_devoir/', afficher_notes_devoir, name='afficher_notes'),
    path('notes_exam/', afficher_notes_exam, name='afficher_notes_exams'),
    path('notes/export/', export_notes_to_excel, name='export_notes_to_excel'),
    path('notes/print/', print_notes, name='print_notes'),
]