from django.db import models
from django.forms import ValidationError
from students.models import Grade, SessionYearModel, Student, Classe, Subject,Composition

class Exam(models.Model):
    name = models.CharField(max_length=100)  # e.g., "1ère composition"
    school_year = models.CharField(max_length=9)  # e.g., "2023/2024"
    date = models.DateField()

    def __str__(self):
        return f"{self.name} - {self.school_year}"


class NoteDevoir(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="notes")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)
    sessionyear = models.ForeignKey(SessionYearModel, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="notes")
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
        composition = models.ForeignKey(Composition, on_delete=models.CASCADE, related_name='notecomposition')
        grade= models.ForeignKey(Grade,on_delete=models.CASCADE)
        classe = models.ForeignKey(Classe,on_delete=models.CASCADE)
        student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='notecompositions')  # L'étudiant
        subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='notecompositions')  # La matière
        sessionyear = models.ForeignKey(SessionYearModel, on_delete=models.CASCADE)
        score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Score de l'examen, peut être null si non évalué
        remarks = models.TextField(null=True, blank=True)  # Commentaires supplémentaires sur la composition (facultatif)

        def clean(self):
            if self.score and (self.score < 0 or self.score > 20):
                raise ValidationError("Le resultat doit etre entre 0 et 20.")
            
        def get_weighted_score(self):
            """Calculer le score pondéré basé sur le coefficient du sujet. Le score est sur 20."""
            if self.score is not None:
            # Assure-toi que le score est sur 20
                score_on_20 = (self.score / 20) * self.subject.coefficient
            return score_on_20  # Score pondéré basé sur le coefficient
            return None  # Si aucun score, retourne None

        def __str__(self):
            return f"Composition for {self.student.first_name} {self.student.last_name} in {self.subject.name} on {self.sessionyear}"

