# views authentification
import json
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.db.models import Sum
from django.utils.translation import gettext as _
from Auth.models import CustomUser
from accounting.models import CashRegister, Fee, Payment, Transaction
from notes.models import NoteDevoir
from students.models import Assignment,Parent, Student, Teacher
from .decorators import role_required
from django.utils.timezone import now
from django.contrib.auth import login
from django.contrib.auth import get_user_model

#login view Api



def user_login(request):
    if request.user.is_authenticated:
        # Redirect based on role if already logged in
        if request.user.role == 'Super Admin':
            return redirect('index')
        elif request.user.role == 'Admins':
            return redirect('dashs')
        elif request.user.role == 'Adminf':
            return redirect('dashf')
        elif request.user.role == 'Professor':
            return redirect('professor_dashboard')
        elif request.user.role == 'Student':
            return redirect('student_dashboard')  # Corrected: Redirect to student dashboard
        elif request.user.role == 'Parent':  # Handle Parent role separately
            try:
                parent = get_object_or_404(Parent, user=request.user)
                student = parent.children.first()  # Get the first linked student
                if student:
                    return redirect('parent_student_dashboard')
                else:
                    messages.error(request, "Aucun étudiant lié à ce compte.")
                    return redirect('login')
            except Parent.DoesNotExist:
                messages.error(request, "Aucun parent trouvé.")
                return redirect('login')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f"Bienvenue, {user.first_name} {user.last_name}!")
            # Redirect based on role
            if user.role == 'Super Admin':
                return redirect('index')
            elif user.role == 'Admins':
                return redirect('dashs')
            elif user.role == 'Adminf':
                return redirect('dashf')
            elif user.role == 'Professor':
                return redirect('professor_dashboard')
            elif user.role == 'Student':
                return redirect('student_dashboard')  # Corrected: Redirect to student dashboard
            elif user.role == 'Parent':  # Handle Parent role separately
                try:
                    parent = get_object_or_404(Parent, user=user)
                    student = parent.children.all()
                    if student:
                        return redirect('parent_student_dashboard')
                    else:
                        messages.error(request, "Aucun étudiant lié à ce compte.")
                        return redirect('login')
                except Parent.DoesNotExist:
                    messages.error(request, "Aucun parent trouvé.")
                    return redirect('login')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    return render(request, 'auth/login.html')

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, "Logout successful.")
    return redirect('login')

@login_required
def super_admin_dashboard(request):
    return render(request, 'dashboard/super_admin.html')

@login_required
def admin_dashboard(request):
    return render(request, 'dashboard/admin.html')

@login_required
def dashs(request):
    """Dashboard for Admins."""
    
    return render(request, 'dash/dashs.html')

@login_required
def dashf(request):
    """Dashboard for Adminf."""
    
    #charts
    months_result = Payment.objects.dates('date', 'month')
    months = [month.strftime('%B') for month in months_result]
    income_data = [0] * len(months_result)
    expense_data = [0] * len(months_result)
    cash_register = CashRegister.objects.filter(user=request.user).first()
    transactions5 = list(Transaction.objects.filter(cash_register=cash_register).order_by('-date')[:5])
    transactions1 = Transaction.objects.filter(cash_register=cash_register).order_by('-date')
    transactions = Transaction.objects.filter(cash_register=cash_register).order_by('-date')[:2]
    transactions = list(transactions)  # Convert to a list to avoid further queryset operations
    student_fees = list(Payment.objects.all().order_by('-date')[:5])
    #count the total of payment this month
    # Calculate the total payment amount for the current month
    current_month = now().month
    current_year = now().year
    total_payments_this_month = Payment.objects.filter(date__year=current_year, date__month=current_month).aggregate(Sum('amount'))['amount__sum'] or 0
    if not cash_register:
        messages.error(request, "Aucun registre de caisse trouvé pour cet utilisateur.")
        return redirect('login')  # Redirect to a fallback page

    

    context = {
        'cash_register': cash_register,
        'current_balance': cash_register.current_balance,
        'total_transactions': transactions1.count(),
        'total_income': transactions1.filter(transaction_type='Credit').aggregate(Sum('amount'))['amount__sum'] or 0,
        'total_expenses': transactions1.filter(transaction_type='Debit').aggregate(Sum('amount'))['amount__sum'] or 0,
        'total_balance': cash_register.current_balance + (transactions1.filter(transaction_type='Credit').aggregate(Sum('amount'))['amount__sum'] or 0) - (transactions1.filter(transaction_type='Debit').aggregate(Sum('amount'))['amount__sum'] or 0),
        'student_fees': student_fees,
        'total_payments_this_month': total_payments_this_month,
        'transactions': transactions5,
        'months_json': json.dumps(months),
        'income_data_json': json.dumps(income_data),
        'expense_data_json': json.dumps(expense_data),}
    return render(request, 'dash/dashf.html', context)

@login_required
def professor_dashboard(request):
    # Get the CustomUser instance (the logged-in user)
    user = request.user

    # Get the Teacher instance associated with the user
    teacher = get_object_or_404(Teacher, user=user)

    # Corrected: Filter assignments by teacher (the logged-in user)
    assignments = Assignment.objects.filter(teacher=user)

    # Corrected: Get classes taught by the teacher
    classes = teacher.classes.all()

    # Get students in the teacher's classes
    students = Student.objects.filter(student_class__in=classes)

    # Get subjects taught by the teacher
    subjects = teacher.subject.all()

    context = {
        'assignments': assignments,
        'classes': classes,
        'students': students,
        'subjects': subjects,
    }
    return render(request, 'teachers/dash_teacher.html', context)

#parents dashboard
@login_required
def parent_student_dashboard(request):
    try:
        parent = request.user.parent  # Assuming you have a OneToOneField from CustomUser to Parent
    except Parent.DoesNotExist:
        messages.error(request, "Vous n'êtes pas un parent.")
        return render(request, 'error_template.html', {'message': 'You are not a parent.'})

    students = parent.children.all()

    students_data = [
        {
            'student': student,
            'siblings': Student.objects.filter(parents__in=student.parents.all()).exclude(pk=student.pk),
            'payments': Fee.objects.filter(student=student).order_by('-due_date'),
            'total_paid': Fee.objects.filter(student=student, paid=True).count(),
            'parent': parent,
        }
        for student in students
    ]

    context = {'students_data': students_data,
               'parent': parent,
               }
    return render(request, 'dash/dashp.html', context)

#students dashboard
@login_required
def student_dashboard(request):
    # Check if the user is authenticated and has the 'Student' role
    print(f"User role: {request.user.role}")  # Debugging
    if request.user.role != 'Student':
        return redirect('error_page')
    try:
        # Get the student object associated with the logged-in user
        student = request.user.student  # Assuming you have a OneToOneField from CustomUser to Student
    except Student.DoesNotExist:
        # Handle the case where the user is not a student
        return render(request, 'error_template.html', {'message': 'You are not a student.'})

    # Retrieve assignments and grades for the student
    assignments = Assignment.objects.filter(classroom=student.student_class)

    # Retrieve payment history from the accounting app
    payments = Fee.objects.filter(student=student).order_by('-due_date')
    # Get the student's notes
    notes = NoteDevoir.objects.filter(student=student).order_by('-id')

    # Prepare the context
    context = {
        'student': student,
        'assignments': assignments,
        'payments': payments,
        'notes': notes,
    }

    return render(request, 'students/index/student_dashboard.html', context)

@role_required('Super Admin')
def super_admin_dashboard(request):
    return render(request, 'dashboard/super_admin.html')

def error_page(request):
    """Render an error page."""
    return render(request, 'error_template.html', {'message': _("An error occurred")})