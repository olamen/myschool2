import logging
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from Auth.models import CustomUser, RoleChoices
from .models import Assignment, Teacher
from .forms import AssignmentForm, TeacherForm
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _



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
    messages.success(request, _("The teacher %(teacher_name)s has been successfully archived!") % {'teacher_name': teacher.name})
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
    messages.success(request, _("The teacher %(teacher_name)s has been successfully restored!") % {'teacher_name': teacher.name})
    return redirect('teacher_archived_list')

@login_required
def assignment_list(request):
    """View to display a list of all assignments."""
    assignments = Assignment.objects.filter(teacher=request.user,is_active=True)  # Filter assignments by the logged-in teacher
    print(f"Assignments for teacher {request.user.username}: {assignments}")  # Debugging line
    return render(request, 'teachers/assignments/assigment_list.html', {'assignments': assignments})

@login_required
def assignment_create_update_view(request,pk=None):
    if pk:
        assignment = get_object_or_404(Assignment, pk=pk)
    else:
        assignment = None
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES, instance=assignment)
        if form.is_valid():
            new_assignment = form.save(commit=False)
            new_assignment.teacher = request.user
            new_assignment.save()
            messages.success(request, _("Operation Finished with success!"))
            return redirect('assignments_list')
    else:
        form = AssignmentForm(instance=assignment)
    return render(request, 'teachers/assignments/assignment_form.html', {'form': form})
def assignment_delete(request, pk):
    """View to delete an assignment."""
    assignment = get_object_or_404(Assignment, pk=pk)
    if request.method == 'POST':
        assignment.delete()
        messages.success(request, _("Assignment deleted successfully!"))
        return redirect('assignments_list')
    return render(request, 'teachers/assignments/assignment_confirm_delete.html', {'assignment': assignment})

@login_required
def assignment_detail(request, pk):
    """View to display the details of an assignment."""
    assignment = get_object_or_404(Assignment, pk=pk)
    return render(request, 'teachers/assignments/assignment_detail.html', {'assignment': assignment})

logger = logging.getLogger(__name__)

@login_required
def archive_or_restore_assignment(request, pk):
    """View to archive or restore an assignment with debug logging."""
    logger.debug(f"Received request to toggle assignment {pk}")

    if not request.user.is_authenticated:
        logger.warning("Unauthorized attempt to toggle assignment")
        return JsonResponse({'status': 'error', 'message': _("Authentication required")}, status=403)

    assignment = get_object_or_404(Assignment, pk=pk)
    print(f"Assignment before toggle: {assignment.is_active}")  # Debugging line

    if request.method == 'POST':
        assignment.is_active = not assignment.is_active  # Toggle status
        assignment.save()
        
        status_message = _("Assignment restored successfully!") if assignment.is_active else _("Assignment archived successfully!")
        logger.info(f"Assignment {pk} status changed: {status_message}")

        return JsonResponse({'status': 'success', 'message': status_message})  # Explicitly return JSON response

    logger.error("Invalid request method for toggling assignment")
    return JsonResponse({'status': 'error', 'message': _("Invalid request")}, status=400)

@login_required
def check_nni(request):
    """Check if the NNI already exists in the database."""
    nni = request.GET.get('nni', '')
    exists = CustomUser.objects.filter(nni=nni).exists()
    print(f"NNI check: {nni}, exists: {exists}")
    return JsonResponse(as_crypsyfied={'nni': exists})


