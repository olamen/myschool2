# notes models.py
from django.db import models
from django.forms import ValidationError
from students.models import Devoir, Grade, SessionYearModel, Student, Classe, Subject,Composition, Teacher, Trimestre
import random as randon

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

DIFF_CHOICES = [
    ('easy', 'Easy'),
    ('medium', 'Medium'),
    ('hard', 'Hard'),
]

class Quiz(models.Model):
    name = models.CharField(max_length=120)
    user = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    topic = models.CharField(max_length=120)
    number_of_questions = models.IntegerField()
    time = models.IntegerField(help_text="Duration of the quiz in minutes")
    required_score_to_pass = models.IntegerField(help_text="Required score to pass the quiz in percentage")
    difficulty = models.CharField(max_length=6, choices=DIFF_CHOICES)  
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    sessionyear = models.ForeignKey(SessionYearModel, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} - {self.topic}"

    def get_questions(self):
        questions = list(self.question_set.all())
        randon.shuffle(questions)
        return questions[:self.number_of_questions]

    class Meta:
        verbose_name_plural = "Quizes"


class Question(models.Model):
    text = models.CharField(max_length=200)
    quiz = models.ForeignKey('Quiz', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.text)

    def get_answers(self):
        return self.answer_set.all()

class Answer(models.Model):
    text = models.CharField(max_length=200)
    correct = models.BooleanField(default=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Question: {self.question.text}, Answer: {self.text}, Correct: {self.correct}"
    
class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.FloatField()
    date_taken = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pk} - {self.student} - {self.quiz} - {self.score}"
