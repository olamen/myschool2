# students/models.py
from django.db import models
from django.core.validators import MinLengthValidator, MinValueValidator


class SessionYearModel(models.Model):
    session_start_year = models.DateField()
    session_end_year = models.DateField()

    def __str__(self):
        return f"{self.session_start_year} to {self.session_end_year}"
 

class Classe(models.Model):
    name = models.CharField(max_length=100, unique=True)
    monthly_salary_fee = models.PositiveIntegerField(null=False)
    is_active = models.BooleanField(default=False) 


    def __str__(self):
        return self.name
    
class Student(models.Model):
    GENDER_CHOICES = [
        ('M', 'Garçon'),
        ('F', 'Fille'),
    ]
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
   
    nni = models.CharField(
        max_length=10, 
        validators=[MinLengthValidator(10)]
    )
    mobile = models.CharField(max_length=40)
    enrollment_date = models.DateField(auto_now_add=True)
    student_class = models.ForeignKey(Classe, on_delete=models.CASCADE, related_name='students')
    has_discount = models.BooleanField(default=False)  # Indicates if the student has a discount
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M')  # Add gender with default 'Garçon'
    photo = models.ImageField(upload_to='student_photos/', blank=True, null=True)  # Optional photo field



    def get_final_fee(self):
        if self.has_discount:
            discount_amount = (self.student_class.monthly_salary_fee * 20) / 100
            return self.student_class.monthly_salary_fee - discount_amount
        return self.student_class.monthly_salary_fee


    def __str__(self):
        return f"{self.first_name} {self.last_name}"
class Parent(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    address = models.TextField(blank=True, null=True)
    children = models.ManyToManyField('Student', related_name='parents')  # Link to multiple students
    photo = models.ImageField(upload_to='parent_photos/', blank=True, null=True)  # Optional photo field


    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.phone_number}"
    
    def get_total_fees(self):
        """
        Calculate the total fees for all students under this parent.
        """
        total_fees = sum(student.fees.filter(paid=False).aggregate(models.Sum('amount_due'))['amount_due__sum'] or 0
                         for student in self.students.all())
        return total_fees

    def get_children_names(self):
        """Get a comma-separated list of children names."""
        return ", ".join([f"{child.first_name} {child.last_name}" for child in self.children.all()])




class Subject(models.Model):
    name = models.CharField(max_length=100)  # Nom du sujet
    class_enrolled = models.ForeignKey(Classe, on_delete=models.CASCADE, related_name='subjects')  # Classe associée
    coefficient = models.DecimalField(max_digits=3, decimal_places=1, default=1)  # Coefficient du sujet
    is_active = models.BooleanField(default=True)  # Statut actif ou inactif
    def __str__(self):
        return f"{self.name} (Coefficient: {self.coefficient})"
    
class Teacher(models.Model):
    SALARY_TYPE_CHOICES = [
        ('hourly', 'Hourly'),
        ('monthly', 'Monthly'),
    ]

    name = models.CharField(max_length=100)
    subject = models.ForeignKey(
        Subject, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='teachers'
    )  # Relationship with Subject model
    enrollment_date = models.DateField()
    salary = models.PositiveIntegerField(null=False)
    salary_type = models.CharField(
        max_length=10,
        choices=SALARY_TYPE_CHOICES,
        default='monthly'
    )  # Field to specify salary type
    is_active = models.BooleanField(default=False)

    def calculate_monthly_salary(self, hours_worked=0):
        """
        Calculate the monthly salary based on the salary type.
        For hourly salary, hours_worked must be provided.
        """
        if self.salary_type == 'hourly':
            if hours_worked <= 0:
                raise ValueError("Hours worked must be greater than 0 for hourly salary.")
            return self.salary * hours_worked
        # If salary type is monthly, return the base salary
        return self.salary

    def __str__(self):
        return self.name


class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')  # Étudiant
    date = models.DateField()  # Date de l'absence ou présence
    status = models.CharField(
        max_length=10, 
        choices=[('Present', 'Present'), ('Absent', 'Absent')],  # Choix de statut
        default='Absent'  # Par défaut, l'étudiant est absent
    )
    class_enrolled = models.ForeignKey(Classe, on_delete=models.CASCADE)  # La classe à laquelle l'étudiant appartient

    def __str__(self):
         return f"Attendance for {self.student.first_name} {self.student.last_name} on {self.date}"
    
class AppConfig(models.Model):
    school_name = models.CharField(max_length=255)
    address = models.TextField()
    contact_number = models.CharField(max_length=15)
    email = models.EmailField()
    website = models.URLField(blank=True, null=True)
    about = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Configuration for {self.school_name}"
    
 #devoir   
class Homework(models.Model):
    name = models.CharField(max_length=100,default="Devoir")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='homeworks')  # L'étudiant
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='homeworkssub')  # La matière
    due_date = models.DateField()  # Date d'échéance
    description = models.TextField()  # Description du devoir
    submission_date = models.DateField(null=True, blank=True)  # Date de soumission du devoir
    submitted = models.BooleanField(default=False)  # Statut de soumission
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Score du devoir, null si pas encore noté

    def get_weighted_score(self):
        """Calculer le score pondéré basé sur le coefficient du sujet. Le score est sur 20."""
        if self.score is not None:
            # Assure-toi que le score est sur 20
            score_on_20 = (self.score / 20) * self.subject.coefficient
            return score_on_20  # Score pondéré basé sur le coefficient
        return None  # Si aucun score, retourne None

    def __str__(self):
        return f"Homework for {self.student} in {self.subject.name}"
    
class Composition(models.Model):
        name = models.CharField(max_length=100,default="Composition")
        student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='compositions')  # L'étudiant
        subject = models.ForeignKey('Subject', on_delete=models.CASCADE, related_name='compositions')  # La matière
        exam_date = models.DateField()  # La date de l'examen
        score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Score de l'examen, peut être null si non évalué
        remarks = models.TextField(null=True, blank=True)  # Commentaires supplémentaires sur la composition (facultatif)
        def get_weighted_score(self):
            """Calculer le score pondéré basé sur le coefficient du sujet. Le score est sur 20."""
            if self.score is not None:
            # Assure-toi que le score est sur 20
                score_on_20 = (self.score / 20) * self.subject.coefficient
            return score_on_20  # Score pondéré basé sur le coefficient
            return None  # Si aucun score, retourne None

        def __str__(self):
            return f"Composition for {self.student.first_name} {self.student.last_name} in {self.subject.name} on {self.exam_date}"