# students/models.py
from decimal import Decimal
from django.db import models
from django.core.validators import MinLengthValidator,RegexValidator ,MinValueValidator
from django.core.exceptions import ValidationError
from Auth.models import CustomUser
from school_management import settings  # Update the import to your CustomUser location
from django.utils.translation import gettext_lazy as _


class SessionYearModel(models.Model):
    name= models.CharField(max_length=100, unique=True, null=True, verbose_name=_("Name"))
    is_current = models.BooleanField(default=False, verbose_name=_("Is Current"))
    session_start_year = models.DateField(verbose_name=_("Session Start Year"))
    session_end_year = models.DateField(verbose_name=_("Session End Year"))
    def clean(self):
        if self.is_current:
            # Ensure only one session year can be marked as current
            if SessionYearModel.objects.filter(is_current=True).exclude(id=self.id).exists():
                raise ValidationError(_("Only one session year can be marked as current."))
    def save(self, *args, **kwargs):
        self.full_clean()
        super(SessionYearModel, self).save(*args, **kwargs)
    def __str__(self):
        return f"{self.name} ({'Current' if self.is_current else 'Past'})"
    
 

class Grade(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Name"))
    def __str__(self):
        return self.name

class Classe(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Name"))
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='grade', default=1, verbose_name=_("Grade"))
    monthly_salary_fee = models.PositiveIntegerField(null=False, verbose_name=_("Monthly Salary Fee"))
    order = models.PositiveIntegerField(null=True, blank=True, unique=True, verbose_name=_("Order"))  # 1 pour la première classe, 2 pour la deuxième, etc.
    is_active = models.BooleanField(default=False, verbose_name=_("Is Active"))


    def __str__(self):
        return self.name
    
class Student(models.Model):
    GENDER_CHOICES = [
        ('M', _('Male')),
        ('F', _('Female')),
    ]
    
    first_name = models.CharField(max_length=100, verbose_name=_("First Name"))
    last_name = models.CharField(max_length=100, verbose_name=_("Last Name"))
    nni = models.CharField(
        max_length=10,
        unique=True,
        validators=[MinLengthValidator(10)],
        verbose_name=_("NNI")
    )
    mobile = models.CharField(max_length=40, verbose_name=_("Mobile"))
    enrollment_date = models.DateField(auto_now_add=True, verbose_name=_("Enrollment Date"))
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student', verbose_name=_("User"))
    student_class = models.ForeignKey(Classe, on_delete=models.CASCADE, related_name='students', verbose_name=_("Class"))
    registration_fee = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=10000, 
        editable=False,  # Prevent users from editing it manually
        verbose_name=_("Registration Fee")
    )
    has_discount = models.CharField(
        max_length=10,
        choices=[
            ('0%', _('0%')),
            ('05%', _('05%')),  # Add 0% option
            ('10%', _('10%')),
            ('20%', _('20%')),
            ('30%', _('30%')),
            ('50%', _('50%')),
            ('100%', _('100%')),
        ],
        default='0%',  # Change default to 0%
        verbose_name=_("Discount")
    )  # Indicates if the student has a discount
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M', verbose_name=_("Gender"))  # Add gender with default 'Garçon'
    photo = models.ImageField(upload_to='student_photos/', blank=True, null=True, verbose_name=_("Photo"))  # Optional photo field
    bio = models.TextField(blank=True, null=True, verbose_name=_("Bio"))  # Optional bio field
    
    #calcule moyenne annuelle de l'etudiant
    def calculate_yearly_average(self):
        # Calculer la moyenne annuelle
        from django.db.models import Avg
        average = self.notecomposition_set.all().aggregate(Avg('score'))['score__avg'] or Decimal('0.0')
        return round(average, 2)  # Arrondir à 2 décimales


    def get_final_fee(self):
        discount_mapping = {
            '05%': 0.05,
            '10%': 0.10,
            '20%': 0.20,
            '30%': 0.30,
            '50%': 0.50,
            '100%': 0.00,
        }
        
        discount_rate = discount_mapping.get(self.has_discount, 0)
        
        print(f"Student: {self.first_name} {self.last_name}")
        print(f"Stored has_discount: {self.has_discount}")
        print(f"Discount rate: {discount_rate}")
        print(f"Monthly fee: {self.student_class.monthly_salary_fee}")
        
        discount_amount = self.student_class.monthly_salary_fee * discount_rate
        final_fee = self.student_class.monthly_salary_fee - discount_amount
        
        print(f"Final fee after discount: {final_fee}")
        
        return final_fee



    def __str__(self):
        return f"{self.first_name} {self.last_name}"
class Parent(models.Model):
    first_name = models.CharField(max_length=100, verbose_name=_("First Name"))
    last_name = models.CharField(max_length=100, verbose_name=_("Last Name"))
    nni = models.CharField(
        max_length=10, 
        validators=[MinLengthValidator(10)],
        unique=True,
        default="1234567890",
        verbose_name=_("NNI")
    )
    email = models.EmailField(unique=True, verbose_name=_("Email"))
    phone_number = models.CharField(max_length=15, verbose_name=_("Phone Number"))
    address = models.TextField(blank=True, null=True, verbose_name=_("Address"))
    children = models.ManyToManyField('Student', related_name='parents', verbose_name=_("Children"))  # Link to multiple students
    photo = models.ImageField(upload_to='parent_photos/', blank=True, null=True, verbose_name=_("Photo"))  # Optional photo field
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_("User"))


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
    name = models.CharField(max_length=100, verbose_name=_("Name"))  # Subject name
    grade = models.ForeignKey('Grade', on_delete=models.CASCADE, related_name='subjects', verbose_name=_("Grade"))  # Associated grade
    points = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Points"))  # Points (for primary)
    coefficient = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, verbose_name=_("Coefficient"))  # Coefficient (for secondary and lycée)
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))  # Active status

    def __str__(self):
        return f"{self.name} ({self.grade.name})"

    def clean(self):
        # Ensure only points or coefficient is used based on the grade
        if self.grade.name.lower() == 'primaire' and self.points is None:
            raise ValidationError(_("Primary subjects must have points."))
        elif self.grade.name.lower() in ['second', 'lycée'] and self.coefficient is None:
            raise ValidationError(_("Secondary or lycée subjects must have coefficients."))
    
class Teacher(models.Model):
    SALARY_TYPE_CHOICES = [
        ('hourly', _('Hourly')),
        ('monthly', _('Monthly')),
    ]
    subject = models.ManyToManyField('Subject', through='TeacherSubject', related_name='teachers', blank=True, verbose_name=_("Subject"))
    classes = models.ManyToManyField('Classe', related_name='teachers', blank=True, verbose_name=_("Classes"))  # Add this line
    photo = models.ImageField(upload_to='parent_teacher/', blank=True, null=True, verbose_name=_("Photo"))  # Optional photo field
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    nni = models.CharField(
        max_length=10, unique=True,
        validators=[MinLengthValidator(10)],
        default="1234567890",
        verbose_name=_("NNI")
    )
    telephone = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex=r'^[234]\d{7}$')],
        blank=True,
        null=True,
        verbose_name=_("Telephone")
    )
    enrollment_date = models.DateField(verbose_name=_("Enrollment Date"))
    salary = models.PositiveIntegerField(null=False, verbose_name=_("Salary"))
    salary_type = models.CharField(
        max_length=10,
        choices=SALARY_TYPE_CHOICES,
        default='monthly',
        verbose_name=_("Salary Type")
    )  # Field to specify salary type
    is_active = models.BooleanField(default=False, verbose_name=_("Is Active"))
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_("User"))
    def get_classes(self):
        # Assuming there's a reverse relation from Classe to Teacher
        return ", ".join([classe.name for classe in self.classes.all()])
    
    def nnivalidator(self):
        nni = self.nni
        # Validate NNI: it should be a 10-digit number
        if not nni.isdigit() or len(nni) != 10:
            raise ValidationError(
                _('%(value)s is not a valid NNI. It should be a 10-digit number.'),
                params={'value': nni},
            )
        return nni

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
    
    def get_subjects(self):
        return ", ".join([subject.name for subject in self.subject.all()])

    def __str__(self):
        return self.name
# teacher_subject relation table
class TeacherSubject(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name=_("Teacher"))
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name=_("Subject"))

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances', verbose_name=_("Student"))  # Étudiant
    date = models.DateField(verbose_name=_("Date"))  # Date de l'absence ou présence
    status = models.CharField(
        max_length=10, 
        choices=[('Present', _('Present')), ('Absent', _('Absent'))],  # Choix de statut
        default='Absent',  # Par défaut, l'étudiant est absent
        verbose_name=_("Status")
    )
    class_enrolled = models.ForeignKey(Classe, on_delete=models.CASCADE, verbose_name=_("Class"))  # La classe à laquelle l'étudiant appartient

    def __str__(self):
         return f"Attendance for {self.student.first_name} {self.student.last_name} on {self.date}"
    
class AppConfig(models.Model):
    school_name = models.CharField(max_length=255, verbose_name=_("School Name"))
    address = models.TextField(verbose_name=_("Address"))
    contact_number = models.CharField(max_length=15, verbose_name=_("Contact Number"))
    email = models.EmailField(verbose_name=_("Email"))
    website = models.URLField(blank=True, null=True, verbose_name=_("Website"))
    about = models.TextField(blank=True, null=True, verbose_name=_("About"))
    def __str__(self):
        return f"Configuration for {self.school_name}"
    
class Trimestre(models.Model):
      name = models.CharField(max_length=100,default="Trimestre",unique=True, verbose_name=_("Name"))
      def __str__(self):
        return f" {self.name}"

 #devoir   
class Devoir(models.Model):
    name = models.CharField(max_length=100,default="Devoir", verbose_name=_("Name"))
    trimestre = models.ForeignKey(Trimestre, on_delete=models.CASCADE,null=True,blank=True, verbose_name=_("Trimester"))
    date = models.DateField(verbose_name=_("Date")) 
    description = models.TextField(verbose_name=_("Description"))  # Description du devoir
    coefficient = models.DecimalField(max_digits=5, decimal_places=2, default=1, verbose_name=_("Coefficient"))  # Score du devoir, null si pas encore noté
    def get_weighted_score(self):
        """Calculer le score pondéré basé sur le coefficient du sujet. Le score est sur 20."""
        if self.coefficient is not None:
            # Assure-toi que le score est sur 20
            score_on_20 = (self.coefficient / 20) * self.subject.coefficient
            return score_on_20  # Score pondéré basé sur le coefficient
        return None  # Si aucun score, retourne None

    def __str__(self):
        return f"Devoir {self.name} in {self.subject.name} for {self.trimestre.name}"
    
class Composition(models.Model):
        name = models.CharField(max_length=100,default="Composition",unique=True, verbose_name=_("Name"))
        trimestre = models.ForeignKey(Trimestre, on_delete=models.CASCADE, default=1, verbose_name=_("Trimester"))
        exam_date = models.DateField(verbose_name=_("Exam Date"))  # La date de l'examen
        coefficient = models.DecimalField(max_digits=4, decimal_places=2, default=1.0, verbose_name=_("Coefficient"))
        remarks = models.TextField(null=True, blank=True, verbose_name=_("Remarks"))  # Commentaires supplémentaires sur la composition (facultatif)
        def get_weighted_score(self):
            if self.coefficient is not None:
                # Assure-toi que le score est sur 20
                score_on_20 = (self.coefficient / 20) * self.subject.coefficient
                return score_on_20  # Score pondéré basé sur le coefficient
            return None  # Si aucun score, retourne None
        def __str__(self):
            return self.name

        
        
class Assignment(models.Model):
    sessionyear = models.ForeignKey(SessionYearModel, on_delete=models.CASCADE, editable=False, blank=True, null=True, verbose_name=_("Session Year"))  # Link to the session year
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Teacher"))  # Link to the teacher (User model)
    classroom = models.ForeignKey(Classe, on_delete=models.CASCADE, verbose_name=_("Classroom"))  # Link to the classroom
    title = models.CharField(max_length=200,verbose_name=_("Title"))  # Title of the assignment
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))  # Optional description
    file = models.FileField(upload_to='assignmentsstudents/', verbose_name=_("File"))  # File upload field
    upload_date = models.DateTimeField(auto_now_add=True, verbose_name=_("Upload Date"))  # Automatically set the upload date
    due_date = models.DateField(blank=True, null=True, verbose_name=_("Due Date"))  # Optional due date
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))  # Active status

    def __str__(self):
        return f"{self.title} - {self.classroom.name} - {self.teacher.first_name} {self.teacher.last_name}"
    


# Schedule model to track class schedules
class Schedule(models.Model):
    """
    Represents a class schedule, tracking courses and modifications.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name=_("User"))
    class_name = models.ForeignKey(Classe, on_delete=models.CASCADE, verbose_name=_("Class Name"))  # Link to the Classe model
    course_name = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name=_("Course Name"))  # Link to the Subject model
    professor = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name=_("Professor"))  # Link to the Teacher model
    start_time = models.TimeField(verbose_name=_("Start Time"))
    end_time = models.TimeField(verbose_name=_("End Time"))

    DAY_CHOICES = [
        ("Monday", _("Monday")),
        ("Tuesday", _("Tuesday")),
        ("Wednesday", _("Wednesday")),
        ("Thursday", _("Thursday")),
        ("Friday", _("Friday")),
    ]
    day_of_week = models.CharField(max_length=10, choices=DAY_CHOICES, verbose_name=_("Day of Week"))

    # Tracking modifications
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Last Updated"))

    #prevent overlapping schedules
    def clean(self):
        # Check for overlapping schedules for the same class and day
        overlapping_schedules = Schedule.objects.filter(
            class_name=self.class_name,
            day_of_week=self.day_of_week,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        ).exclude(id=self.id)
        if overlapping_schedules.exists():
            raise ValidationError(_("This schedule overlaps with an existing schedule for the same class on this day."))

    def __str__(self):
        return f"{self.class_name} - {self.course_name} ({self.day_of_week}, {self.start_time}-{self.end_time})"
