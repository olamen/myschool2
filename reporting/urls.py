from django.urls import path
from .views import exam_list, report_card_pdf, exam_detail , edit_exam

urlpatterns = [
    path("exams/", exam_list, name="exam_list"),
    path("exams/<int:exam_id>/", exam_detail, name="exam_detail"),
    path("exams/<int:exam_id>/edit/", edit_exam, name="edit_exam"),
    path("report_card/<int:student_id>/<int:exam_id>/", report_card_pdf, name="report_card_pdf"),
]