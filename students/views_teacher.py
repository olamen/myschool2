from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from Auth.models import CustomUser, RoleChoices
from .models import Teacher
from .forms import AssignmentForm, TeacherForm
from django.contrib.auth.decorators import login_required


# def teacher_list(request):
#     """View to display a list of all active teachers."""
#     teachers = Teacher.objects.filter(is_active=True)
#     logger.debug(f'Active teachers: {teachers}')
#     print(f'Active teachers: {teachers}')
#     teachers_list = list(teachers.values())
#     return JsonResponse({"teachers": teachers_list})


#crude devoir
@login_required
def teacher_list(request):
    """View to display a list of all active teachers."""
    teachers = Teacher.objects.filter(is_active=True)
    return render(request, 'teachers/teacher_list.html', {'teachers': teachers})

@login_required
def teacher_create_update_view(request, pk=None):
    if pk:
        teacher = get_object_or_404(Teacher, pk=pk)
    else:
        teacher = None

    if request.method == 'POST':
        form = TeacherForm(request.POST, request.FILES, instance=teacher)
        if form.is_valid():
            new_teacher = form.save(commit=False)
            # Create or update a user for the teacher with PROFESSOR role
            if not teacher:
                user = CustomUser.objects.create_user(
                    username=new_teacher.nni,
                    password='defaultpassword',  # You should generate a secure password or allow the teacher to set it
                    first_name=new_teacher.name,
                    email='',  # Add email field if available
                )
                user.is_approved = True
                user.role = RoleChoices.PROFESSOR
                user.save()
                new_teacher.user = user
            else:
                new_teacher.user.nni = new_teacher.nni  # Update existing user's nni if it has changed
                new_teacher.user.first_name = new_teacher.name  # Update existing user's name if it has changed
                new_teacher.user.image = new_teacher.photo  # Update existing user's image if it has changed
                new_teacher.user.save()
            new_teacher.save()
            return redirect('teachers_list')  # Assuming you have a teacher list view
    else:
        form = TeacherForm(instance=teacher)

    return render(request, 'teachers/teacher_form.html', {'form': form})

@login_required
def teacher_archive(request, pk):
    """View to archive a teacher instead of deleting."""
    teacher = get_object_or_404(Teacher, pk=pk)
    teacher.is_active = False
    teacher.save()
    messages.success(request, f"L'enseignant {teacher.name} a été archivé avec succès !")
    return redirect('teachers_list')

@login_required
def teacher_archived_list(request):
    """View to display a list of archived teachers."""
    teachers = Teacher.objects.filter(is_active=False)
    return render(request, 'teachers/teacher_archived_list.html', {'teachers': teachers})

@login_required
def teacher_restore(request, pk):
    """View to restore an archived teacher."""
    teacher = get_object_or_404(Teacher, pk=pk)
    teacher.is_active = True
    teacher.save()
    messages.success(request, f"L'enseignant {teacher.name} a été restauré avec succès !")
    return redirect('teacher_archived_list')


@login_required
def upload_assignment(request):
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.teacher = request.user  # Set the teacher to the current user
            assignment.save()
            return redirect('teacher_dashboard')  # Redirect to the teacher dashboard
    else:
        form = AssignmentForm()
    return render(request, 'upload_assignment.html', {'form': form})