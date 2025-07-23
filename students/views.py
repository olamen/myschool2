# students/views.py
from datetime import date
import datetime
from decimal import Decimal
from django.http import HttpResponseForbidden, JsonResponse
from rest_framework import viewsets
from rest_framework.renderers import TemplateHTMLRenderer
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Sum, Count
from accounting.models import  CashRegister, ChargeType, Fee, Payment, Transaction
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import action
from django.contrib.auth import authenticate, login
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib import messages
from django.utils import timezone
from Auth.models import CustomUser, RoleChoices
from rest_framework.permissions import BasePermission

from students.forms import StudentForm
from .models import AppConfig, Grade, Devoir, Student, Subject, Teacher, Classe, SessionYearModel, Attendance, Composition
from .serializers import AppConfigSerializer , StudentSerializer, SubjectSerializer, TeacherSerializer, ClassSerializer, SessionYearSerializer, AttendanceSerializer
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from django.utils.timezone import now
from django.db import transaction
from django.utils.translation import gettext as _


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

#grade
@login_required
def add_grade(request):
    if request.method == 'POST':
        name = request.POST['name']
        Grade.objects.create(name=name)
        return redirect('grades_list')
    return render(request, 'students/grade_form.html', {'grade': None})
@login_required
def grades_list(request):
    grades = Grade.objects.all()
    return render(request, 'students/grades_list.html', {'grades': grades})
@login_required
def update_grade(request, grade_id):
    grade = get_object_or_404(Grade, id=grade_id)
    if request.method == 'POST':
        grade.name = request.POST['name']
        grade.save()
        return redirect('grades_list')
    return render(request, 'students/grade_form.html', {'grade': grade})



#end Grade

@login_required
def update_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    grades = Grade.objects.all()  # Fetch all grades
    classes = Classe.objects.filter(grade=student.student_class.grade)  # Fetch classes under the student's grade

    if request.method == 'POST':
        student.first_name = request.POST.get('first_name', student.first_name)
        student.last_name = request.POST.get('last_name', student.last_name)
        student.nni = request.POST.get('nni', student.nni)
        student.mobile = request.POST.get('mobile', student.mobile)
        student.enrollment_date = request.POST.get('enrollment_date', student.enrollment_date)
        student.gender = request.POST.get('gender', student.gender)
        student.has_discount = 'has_discount' in request.POST

        grade_id = request.POST.get('grade')
        class_id = request.POST.get('student_class')

        if grade_id:
            selected_grade = get_object_or_404(Grade, id=grade_id)
            classes = Classe.objects.filter(grade=selected_grade)
            if class_id:
                student.student_class = get_object_or_404(Classe, id=class_id)

        if 'photo' in request.FILES:
            student.photo = request.FILES['photo']

        student.save()
        messages.success(request, "Student updated successfully!")
        return redirect('students_list')  # Redirect to a student list or desired page
    context = {
        'student': student,
        'grades': grades,
        'classes': classes,
    }

    return render(request, 'students/update_student.html', context)

@login_required
def indexview(request):
    # Redirect based on role if logged in
    if request.user.role == 'Super Admin':
        # This is the correct page for Super Admin; no redirect needed
        pass
    elif request.user.role == 'Admins':
        messages.success(request, "Welcome to the Admin dashboard!")
        return redirect('dashs')
    elif request.user.role == 'Adminf':
        messages.success(request, "Welcome to the finance dashboard!")
        return redirect('dashf')
    elif request.user.role == 'Professor':
        messages.success(request, "Welcome to the Teacher dashboard!")
        return redirect('professor_dashboard')
    elif request.user.role == 'Parent/Student':
        messages.success(request, "Welcome to the Parent dashboard!")
        return redirect('parent_student_dashboard')
    elif request.user.role == 'Student':
        messages.success(request, "Welcome to the Student dashboard!")
        return redirect('student_dashboard')

    # Logic for the Super Admin view
    total_students = Student.objects.count()
    total_subjects = Subject.objects.count()
    total_teachers = Teacher.objects.count()
    students = Student.objects.all().order_by('-id')[:5]
    clsses = Classe.objects.count()
    transactions = Transaction.objects.all().order_by('-date')


    # Get the count of students per class
    class_counts = Classe.objects.annotate(student_count=Count('students'))
    from django.utils.translation import get_language

    context = {
        'total_students': total_students,
        'total_subjects' : total_subjects,
        'total_teachers': total_teachers,
        'class_counts': class_counts,
        'clsses_counts': clsses,
        'transactions':     transactions,
        'students' : students,
        'hello': _('Welcome to the Super Admin Dashboard'),

    }
    return render(request, 'index.html', context)




@login_required
def student_fees_by_month(request):
    # Calculer la date il y a 12 mois à partir d'aujourd'hui
    # Convert today's date to a timezone-aware datetime object
    #print('Payment:',Payment.objects.all().values('date', 'amount'))

    today = now()
    start_date = today - timedelta(days=365)

    # Fetch payments within the last 12 months
    payments_by_month = (
        Payment.objects.filter(date__gte=start_date, date__lte=today)
        .values('date__month', 'date__year')
        .annotate(total_amount=Sum('amount'))
    )

    #print(payments_by_month)

    # Créer un tableau des 12 derniers mois avec des valeurs par défaut à 0
    fees_data = [0] * 12
    current_month = today.month
    current_year = today.year

    for payment in payments_by_month:
        # Calculer l'index correct pour les 12 derniers mois
        month_diff = (current_year - payment['date__year']) * 12 + (current_month - payment['date__month'])
        if 0 <= month_diff < 12:
            fees_data[11 - month_diff] = float(payment['total_amount'])

    return JsonResponse({"series": fees_data})


    
    
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
        clsses = Classe.objects.count()

        # Get the count of students per class
        class_counts = Classe.objects.annotate(student_count=Count('students'))

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
        return render(request, 'students/studentlist.html', {'students': students})

   
    @action(detail=True, methods=['get'], renderer_classes=[TemplateHTMLRenderer])
    def student_detail(self, request, pk=None):
        """View to display details about a specific student."""
        student = self.get_object()

        # Retrieve siblings (students with the same parent accounts)
        siblings = Student.objects.filter(parents__in=student.parents.all()).exclude(pk=student.pk)

        # Retrieve payment history from the accounting app 
        payments = Fee.objects.filter(student=student).order_by('-due_date')

        # Retrieve transaction history
        #transactions = Transaction.objects.filter(student=student).order_by('-date')

        context = {
            'student': student,
            'siblings': siblings,
            'payments': payments,
            #'transactions': transactions,
            'parents': student.parents.all(),  # Get all parents linked to the student
        }
        return render(request, 'students/student_detail.html', context)
        

    @action(detail=False, methods=['get', 'post'], renderer_classes=[TemplateHTMLRenderer])
    def add_student(self, request):
        """Render and process the form to add a student using Django's form handling."""
        
        if request.method == 'POST':
            form = StudentForm(request.POST, request.FILES)

            if form.is_valid():
                # Extract form data
                student_class_id = form.cleaned_data['student_class'].id
                nni = form.cleaned_data['nni']

                # Ensure the student class exists
                try:
                    student_class = Classe.objects.get(id=student_class_id)
                except Classe.DoesNotExist:
                    messages.error(request, "Class not found.")
                    return render(request, 'students/add_student.html', {'form': form})

                # Ensure unique NNI
                if CustomUser.objects.filter(username=nni).exists():
                    messages.error(request, "A user with this NNI already exists.")
                    return render(request, 'students/add_student.html', {'form': form})

                # Ensure an open cash register exists
                try:
                    cash_register = CashRegister.objects.get(is_open=True, user=request.user)
                except CashRegister.DoesNotExist:
                    messages.error(request, "No open cash register found.")
                    return render(request, 'students/add_student.html', {'form': form})

                # Process the transaction safely
                with transaction.atomic():
                    # Create a user for the student
                    user = CustomUser.objects.create_user(
                        username=nni,
                        password='defaultpassword',  # Change for better security
                        first_name=form.cleaned_data['first_name'],
                        last_name=form.cleaned_data['last_name'],
                        email='',
                    )
                    user.is_approved = True
                    user.role = RoleChoices.STUDENT
                    user.save()

                    # Create student and set fixed registration fee
                    student = form.save(commit=False)
                    student.user = user
                    student.registration_fee = 10000  # Set fixed fee
                    student.student_class = student_class  # Assign validated class
                    student.save()

                    # Update cash register balance
                    cash_register.update_current_balance(10000, "income")

                messages.success(request, "Student added successfully!")
                return redirect('students_list')

            else:
                messages.error(request, "Please correct the errors below.")

        else:
            form = StudentForm()  # Empty form for GET request
        
        return render(request, 'students/add_student.html', {'form': form})



class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer

class ClassViewSet(viewsets.ModelViewSet):
    queryset = Classe.objects.all()
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
            student_class = Classe.objects.get(id=class_id)
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=404)
        except Classe.DoesNotExist:
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
        

@login_required
def student_create_update_view(request, pk=None):
    student = get_object_or_404(Student, pk=pk) if pk else None
    is_new_student = student is None  # Check if this is a new student

    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            new_student = form.save(commit=False)

            # Create user only for new students
            if is_new_student:
                user = CustomUser.objects.create_user(
                    username=new_student.nni,
                    password='defaultpassword',  # Consider generating a secure password
                    first_name=new_student.first_name,
                    last_name=new_student.last_name,
                    image=new_student.photo,
                    email='',  
                )
                user.is_approved = True
                user.role = RoleChoices.STUDENT
                user.save()
                new_student.user = user

            else:
                new_student.user.nni = new_student.nni  
                new_student.user.first_name = new_student.first_name  
                new_student.user.last_name = new_student.last_name 
                new_student.user.image = new_student.photo  
                new_student.user.save()

            new_student.save()

            # Create a transaction **only if it's a new student**
            if is_new_student:
                cash_register = CashRegister.objects.filter(is_open=True).first()
                transaction = Transaction.objects.create(
                    cash_register=cash_register,
                    amount=Decimal(new_student.registration_fee),  
                    transaction_type='income',  
                    description=f"Registration Fee for {new_student.first_name} {new_student.last_name}",
                    user=new_student.user
                )

                # **Update the Cash Register balance**
                if cash_register:
                    cash_register.update_current_balance(transaction.amount, transaction.transaction_type)
            messages.success(request, "Student created successfully!")
            return redirect('students_list')

    else:
        form = StudentForm(instance=student)
    messages.error(request, "Please correct the errors below.")
    return render(request, 'students/student_form.html', {'form': form})


