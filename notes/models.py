from django.db import models
from students.models import Student, Classe, Subject

class Exam(models.Model):
    name = models.CharField(max_length=100)  # e.g., "1ère composition"
    school_year = models.CharField(max_length=9)  # e.g., "2023/2024"
    date = models.DateField()

    def __str__(self):
        return f"{self.name} - {self.school_year}"


class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="grades")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="grades")
    coefficient = models.DecimalField(max_digits=4, decimal_places=2, default=1.0)
    score = models.DecimalField(max_digits=5, decimal_places=2)

    def get_weighted_score(self):
        return self.score * self.coefficient

    def __str__(self):
        return f"{self.student} - {self.subject} - {self.score}"


class ReportCard(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="report_cards")
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="report_cards")
    total_score = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    average_score = models.DecimalField(max_digits=4, decimal_places=2, default=0.0)
    rank = models.PositiveIntegerField(null=True, blank=True)
    decision = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"Report Card for {self.student} - {self.exam}"