from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .decorators import role_required


def user_login(request):
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
            elif user.role == 'Admin':
                return redirect('admin_dashboard')
            elif user.role == 'Professor':
                return redirect('professor_dashboard')
            else:  # Parent/Student
                return redirect('parent_student_dashboard')
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
def parent_student_dashboard(request):
    return render(request, 'dashboard/parent_student.html')


@role_required('Super Admin')
def super_admin_dashboard(request):
    return render(request, 'dashboard/super_admin.html')