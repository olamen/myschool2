from django.db import models
from students.models import SessionYearModel, Student, Classe, Subject

class Exam(models.Model):
    name = models.CharField(max_length=100)  # e.g., "1ère composition"
    school_year = models.CharField(max_length=9)  # e.g., "2023/2024"
    date = models.DateField()

    def __str__(self):
        return f"{self.name} - {self.school_year}"


class NoteStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="notes")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)
    sessionyear = models.ForeignKey(SessionYearModel, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="notes")
    coefficient = models.DecimalField(max_digits=4, decimal_places=2, default=1.0)
    score = models.DecimalField(max_digits=5, decimal_places=2)

    def get_weighted_score(self):
        return self.score * self.coefficient

    def __str__(self):
        return f"{self.student} - {self.subject} - {self.score}"

