from django.urls import path
from .views import exam_list, report_card_pdf,afficher_notes_devoir

urlpatterns = [
    path("exams/", exam_list, name="exam_list"),
    path("report_card/<int:student_id>/<int:exam_id>/", report_card_pdf, name="report_card_pdf"),
    path('notes_devoir/', afficher_notes_devoir, name='afficher_notes'),
]