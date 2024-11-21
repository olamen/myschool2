from django.contrib.auth.models import AbstractUser
from django.db import models

class RoleChoices(models.TextChoices):
    SUPER_ADMIN = 'Super Admin', 'Super Admin'
    ADMINS = 'Admins', 'Admins'
    ADMINF = 'Adminf', 'Adminf'
    PROFESSOR = 'Professor', 'Professor'
    PARENT_OR_STUDENT = 'Parent/Student', 'Parent/Student'

class CustomUser(AbstractUser):
    is_approved = models.BooleanField(default=False)
    nni = models.CharField(max_length=10, unique=True, editable=False, blank=True,null=True)
    image = models.ImageField(upload_to='user_photos/', blank=True, null=True)
    role = models.CharField(
        max_length=20,
        choices=RoleChoices.choices,
        default=RoleChoices.PARENT_OR_STUDENT
    )

    def __str__(self):
        return f"{self.username} ({self.role})"