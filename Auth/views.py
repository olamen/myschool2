# views authentification
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from accounting.models import Fee
from students.models import Parent, Student
from .decorators import role_required


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
        else:  # Parent/Student
            try:
                parent = get_object_or_404(Parent, user=user)
                student = parent.children.first()  # Get the first linked student
                if student:
                    return redirect('parent_student_dashboard', parent_id=parent.id)
                else:
                    messages.error(request, "Aucun étudiant lié à ce compte.")
                    return redirect('login')
            except Student.DoesNotExist:
                messages.error(request, "Aucun étudiant trouvé.")
                return redirect('login')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f"Bienvenue, {user.username}!")
            # Redirect based on role
            if user.role == 'Super Admin':
                return redirect('index')
            elif user.role == 'Admins':
                return redirect('dashs')
            elif user.role == 'Adminf':
                return redirect('dashf')
            elif user.role == 'Professor':
                return redirect('professor_dashboard')
            else:  # Parent/Student
                try:
                    parent = get_object_or_404(Parent, user=user)
                    student = parent.children.first()  # Get the first linked student
                    if student:
                        return redirect('parent_student_dashboard', parent_id=parent.id)
                    else:
                        messages.error(request, "Aucun étudiant lié à ce compte.")
                        return redirect('login')
                except Student.DoesNotExist:
                    messages.error(request, "Aucun étudiant trouvé.")
                    return redirect('login')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    return render(request, 'auth/login.html')

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, "Déconnexion réussie.")
    return redirect('login')

@login_required
def super_admin_dashboard(request):
    return render(request, 'dashboard/super_admin.html')

@login_required
def admin_dashboard(request):
    return render(request, 'dashboard/admin.html')

@login_required
def professor_dashboard(request):
    return render(request, 'dashboard/professor.html')

@login_required
def parent_student_dashboard(request,parent_id):
    parent = get_object_or_404(Parent, id=parent_id)
    students = parent.children.all()

    students_data = [
        {
            'student': student,
            'siblings': Student.objects.filter(parents__in=student.parents.all()).exclude(pk=student.pk),
            'payments': Fee.objects.filter(student=student).order_by('-due_date'),
        }
        for student in students
    ]

    context = {'students_data': students_data}
    return render(request, 'dashboard/parent_student.html', context)


@role_required('Super Admin')
def super_admin_dashboard(request):
    return render(request, 'dashboard/super_admin.html')