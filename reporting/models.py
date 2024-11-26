from django.db import models
from students.models import Composition, SessionYearModel, Student


class ReportCard(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="report_cards Reporting Card")
    exam = models.ForeignKey(Composition, on_delete=models.CASCADE, related_name="report_cards Reporting Exa")
    sessionyear = models.ForeignKey(SessionYearModel, on_delete=models.SET_NULL)
    total_score = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    average_score = models.DecimalField(max_digits=4, decimal_places=2, default=0.0)
    rank = models.PositiveIntegerField(null=True, blank=True)
    decision = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"Report Card for {self.student} - {self.exam}"