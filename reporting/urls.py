from django.urls import path
from .views import exam_list, report_card_pdf

urlpatterns = [
    path("exams/", exam_list, name="exam_list"),
    path("report_card/<int:student_id>/<int:exam_id>/", report_card_pdf, name="report_card_pdf"),
]