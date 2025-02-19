from django.db import models
from django.forms import ValidationError
from students.models import Devoir, Grade, SessionYearModel, Student, Classe, Subject,Composition, Trimestre

class Exam(models.Model):
    name = models.CharField(max_length=100)  # e.g., "1ère composition"
    school_year = models.CharField(max_length=9)  # e.g., "2023/2024"
    date = models.DateField()
    def __str__(self):
        return f"{self.name} - {self.school_year}"


class NoteDevoir(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="notes")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    sessionyear = models.ForeignKey(SessionYearModel, on_delete=models.CASCADE)
    trimestre = models.ForeignKey(Trimestre,on_delete=models.CASCADE)
    devoir = models.ForeignKey(Devoir, on_delete=models.CASCADE, related_name="notes")
    coefficient = models.DecimalField(max_digits=4, decimal_places=2, default=1.0)
    score = models.DecimalField(max_digits=5, decimal_places=2)

    def clean(self):
            if self.score and (self.score < 0 or self.score > 20):
                raise ValidationError("Le resultat doit etre entre 0 et 20.")

    def get_weighted_score(self):
        return self.score * self.coefficient

    def __str__(self):
        return f"{self.student} - {self.subject} - {self.score}"
    
class NoteComposition(models.Model):
        ABSENCE_CHOICES = [
            (None, 'Présent'),
            ('ABJ', 'Absence Justifiée'),
            ('ABS', 'Absence Non Justifiée'),
        ]
        student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='notecompositions')  # L'étudiant
        subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='notecompositions')  # La matière
        composition = models.ForeignKey(Composition, on_delete=models.CASCADE, related_name='notecomposition')
        sessionyear = models.ForeignKey(SessionYearModel, on_delete=models.CASCADE)
        trimestre = models.ForeignKey(Trimestre,on_delete=models.CASCADE)
        score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Score de l'examen, peut être null si non évalué
        remarks = models.TextField(null=True, blank=True)  # Commentaires supplémentaires sur la composition (facultatif)
        coefficient = models.DecimalField(max_digits=4, decimal_places=2, default=1.0)
        absence = models.CharField(
            max_length=3,
            choices=ABSENCE_CHOICES,
            null=True,
            blank=True,
            verbose_name="Statut de présence"
        )

        def clean(self):
            if self.score and self.absence:
                raise ValidationError("Vous ne pouvez pas à la fois saisir une note et une absence.")
            if not self.score and not self.absence:
                raise ValidationError("Vous devez saisir soit une note soit un statut d'absence.")
            
            if self.score and (self.score < 0 or self.score > 20):
                raise ValidationError("Le résultat doit être entre 0 et 20.")

        def get_weighted_score(self):
            """Retourne None si absence justifiée pour exclusion des calculs"""
            if self.absence == 'ABJ':
                return None
            if self.score is not None:
                return (self.score / 20) * self.subject.coefficient
            return 0 if self.absence == 'ABS' else None  # Gestion des absences non justifiées

        def __str__(self):
            return f"{self.composition.name} on {self.sessionyear}"

