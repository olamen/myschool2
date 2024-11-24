# students/views.py
from django.http import HttpResponseForbidden
from rest_framework import viewsets
from rest_framework.renderers import TemplateHTMLRenderer
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Sum, Count
from accounting.models import Payment, Transaction
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import action
from django.contrib.auth import authenticate, login
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from Auth.models import CustomUser
from rest_framework.permissions import BasePermission
from .models import AppConfig, Homework, Student, Subject, Teacher, Class, SessionYearModel, Attendance, Composition
from .serializers import AppConfigSerializer, CompositionSerializer, HomeworkSerializer, StudentSerializer, SubjectSerializer, TeacherSerializer, ClassSerializer, SessionYearSerializer, AttendanceSerializer


def forbidden_view(request, exception=None):
    """
    Custom view for handling 403 Forbidden errors.
    """
    return HttpResponseForbidden(render(request, '403.html'))

class HasRolePermission(BasePermission):
    """
    Custom permission to grant access based on user roles.
    """
    allowed_roles = []

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in self.allowed_roles
@login_required
def indexview(request):
        """
        Render a dashboard view for students and classes.
        """

        # Restrict access to Super Admin
        HasRolePermission.allowed_roles = ['Super Admin']

        # Get total count of students
        total_students = Student.objects.count()
        clsses = Class.objects.count()

        # Get the count of students per class
        class_counts = Class.objects.annotate(student_count=Count('students'))

        context = {
            'total_students': total_students,
            'class_counts': class_counts,
            'clsses_counts': clsses,
        }
        return render(request, 'index.html', context)


    
    
class IndexViewSet(viewsets.ModelViewSet):
    """
    Index view for managing the dashboard and student summary.
    """
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated, HasRolePermission]
    renderer_classes = [TemplateHTMLRenderer]  # Enable HTML rendering

    @login_required
    @action(detail=False, methods=['get'], renderer_classes=[TemplateHTMLRenderer])
    def index(self, request):
        """
        Render a dashboard view for students and classes.
        """

        # Restrict access to Super Admin
        HasRolePermission.allowed_roles = ['Super Admin']

        # Get total count of students
        total_students = Student.objects.count()
        clsses = Class.objects.count()

        # Get the count of students per class
        class_counts = Class.objects.annotate(student_count=Count('students'))

        context = {
            'total_students': total_students,
            'class_counts': class_counts,
            'clsses_counts': clsses,
        }
        return render(request, 'index.html', context)
        
class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    renderer_classes = [TemplateHTMLRenderer]  # Enable HTML rendering

    @action(detail=False, methods=['get'], renderer_classes=[TemplateHTMLRenderer])
    def student_list(self, request):
        """Render a list of students in an HTML template."""
        students = Student.objects.all()
        return render(request, 'dash/studentlist.html', {'students': students})

   
    @action(detail=True, methods=['get'], renderer_classes=[TemplateHTMLRenderer])
    def student_detail(self, request, pk=None):
        """View to display details about a specific student."""
        student = self.get_object()

        # Retrieve siblings (students with the same parent accounts)
        siblings = Student.objects.filter(parents__in=student.parents.all()).exclude(pk=student.pk)

        # Retrieve payment history from the accounting app
        payments = Payment.objects.filter(student=student).order_by('-payment_date')

        # Retrieve transaction history
        transactions = Transaction.objects.filter(student=student).order_by('-payment_date')

        context = {
            'student': student,
            'siblings': siblings,
            'payments': payments,
            'transactions': transactions,
            'parents': student.parents.all(),  # Get all parents linked to the student
        }
        return render(request, 'students/student_detail.html', context)
        
    @action(detail=False, methods=['get', 'post'], renderer_classes=[TemplateHTMLRenderer])
    def add_student(self, request):
        """Rendre et traiter le formulaire pour ajouter un étudiant."""
        if request.method == 'POST':
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            nni = request.POST.get('nni')
            mobile = request.POST.get('mobile')
            enrollment_date = request.POST.get('enrollment_date')
            student_class_id = request.POST.get('student_class')
            gender = request.POST.get('gender')
            has_discount = request.POST.get('has_discount') == 'on'
            photo = request.FILES.get('photo')  # Handle uploaded photo

            # Vérifie si la classe existe
            try:
                student_class = Class.objects.get(id=student_class_id)
            except Class.DoesNotExist:
                return Response({"error": "Classe introuvable"}, status=404)
            
            # Créer un nouvel étudiant
            Student.objects.create(
                first_name=first_name,
                last_name=last_name,
                nni=nni,
                mobile=mobile,
                enrollment_date=enrollment_date,
                student_class=student_class,
                gender=gender,
                has_discount=has_discount,
                photo=photo  # Save the uploaded photo

            )
            return redirect('students_list')  # Rediriger vers la liste des étudiants

        # Afficher le formulaire si la requête est GET
        classes = Class.objects.all()
        return render(request, 'dash/add_student.html', {'classes': classes})


class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer

class ClassViewSet(viewsets.ModelViewSet):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer

class SessionYearViewSet(viewsets.ModelViewSet):
    queryset = SessionYearModel.objects.all()
    serializer_class = SessionYearSerializer

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    renderer_classes = [TemplateHTMLRenderer]  # Enable HTML rendering

    @action(detail=False, methods=['get'], renderer_classes=[TemplateHTMLRenderer])
    def subject_list(self, request):
        """Render a list of subjects in an HTML template."""
        subjects = Subject.objects.all()
        return render(request, 'dash/dash.html', {'subjects': subjects})

    @action(detail=True, methods=['get'], renderer_classes=[TemplateHTMLRenderer])
    def subject_detail(self, request, pk=None):
        """Render a detailed view of a single subject in an HTML template."""
        subject = self.get_object()
        return render(request, 'subject_detail.html', {'subject': subject})

    @action(detail=False, methods=['post'])
    def mark_attendance(self, request):
        student_id = request.data.get('student_id')
        status = request.data.get('status')  # 'Present' ou 'Absent'
        class_id = request.data.get('class_id')
        
        # Vérifie si l'étudiant et la classe existent
        try:
            student = Student.objects.get(id=student_id)
            student_class = Class.objects.get(id=class_id)
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=404)
        except Class.DoesNotExist:
            return Response({"error": "Class not found"}, status=404)
        
        # Crée un enregistrement de présence
        attendance = Attendance(
            student=student,
            date=timezone.now().date(),  # Date du jour
            status=status,
            class_enrolled=student_class
        )
        attendance.save()

        return Response({"message": "Attendance marked successfully"})
    
class AppConfigViewSet(viewsets.ModelViewSet):
    queryset = AppConfig.objects.all()
    serializer_class = AppConfigSerializer
    def get(self, request):
        try:
            config = AppConfig.objects.all().first()  # Assumes only one configuration instance
            serializer = AppConfigSerializer(config)
            return Response(serializer.data)
        except AppConfig.DoesNotExist:
            return Response({"error": "AppConfig not found"}, status=404)
        

# Vue pour gérer les devoirs
class HomeworkViewSet(viewsets.ModelViewSet):
    queryset = Homework.objects.all()
    serializer_class = HomeworkSerializer

    @action(detail=True, methods=['patch'])
    def update_score(self, request, pk=None):
        """Mettre à jour le score d'un devoir."""
        homework = self.get_object()
        score = request.data.get('score')  # Récupère le score du corps de la requête
        
        if score is not None:
            homework.score = score
            homework.save()
            return Response({"message": "Score updated successfully"})
        else:
            return Response({"error": "Score is required"}, status=400)

    @action(detail=True, methods=['get'])
    def weighted_score(self, request, pk=None):
        """Calculer le score pondéré basé sur le coefficient du sujet."""
        homework = self.get_object()
        weighted_score = homework.get_weighted_score()  # Méthode pour calculer le score pondéré
        return Response({"weighted_score": weighted_score})
    
class CompositionViewSet(viewsets.ModelViewSet):
    queryset = Composition.objects.all()
    serializer_class = CompositionSerializer

    @action(detail=True, methods=['patch'])
    def update_score(self, request, pk=None):
        """Mettre à jour le score d'une composition."""
        composition = self.get_object()
        score = request.data.get('score')  # Récupère le score du corps de la requête
        
        if score is not None:
            composition.score = score
            composition.save()
            return Response({"message": "Score updated successfully"})
        else:
            return Response({"error": "Score is required"}, status=400)

    @action(detail=True, methods=['get'])
    def weighted_score(self, request, pk=None):
        """Calculer le score pondéré basé sur le coefficient du sujet."""
        composition = self.get_object()
        weighted_score = composition.score * composition.subject.coefficient  # Score pondéré
        return Response({"weighted_score": weighted_score})