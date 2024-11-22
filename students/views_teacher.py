from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Teacher

def teacher_list(request):
    """View to display a list of all active teachers."""
    teachers = Teacher.objects.filter(is_active=True)
    return render(request, 'teachers/teacher_list.html', {'teachers': teachers})


def teacher_create(request):
    """View to create a new teacher."""
    if request.method == 'POST':
        name = request.POST.get('name')
        subject = request.POST.get('subject')
        salary = request.POST.get('salary')
        salary_type = request.POST.get('salary_type')
        enrollment_date = request.POST.get('enrollment_date')
        
        Teacher.objects.create(
            name=name,
            subject=subject,
            salary=salary,
            salary_type=salary_type,
            enrollment_date=enrollment_date,
            is_active=True
        )
        messages.success(request, f"L'enseignant {name} a été créé avec succès !")
        return redirect('teacher_list')
    return render(request, 'teachers/teacher_form.html')


def teacher_update(request, pk):
    """View to update an existing teacher."""
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == 'POST':
        teacher.name = request.POST.get('name')
        teacher.subject = request.POST.get('subject')
        teacher.salary = request.POST.get('salary')
        teacher.salary_type = request.POST.get('salary_type')
        teacher.enrollment_date = request.POST.get('enrollment_date')
        teacher.save()
        messages.success(request, f"L'enseignant {teacher.name} a été mis à jour avec succès !")
        return redirect('teacher_list')
    return render(request, 'teachers/teacher_form.html', {'teacher': teacher})


def teacher_archive(request, pk):
    """View to archive a teacher instead of deleting."""
    teacher = get_object_or_404(Teacher, pk=pk)
    teacher.is_active = False
    teacher.save()
    messages.success(request, f"L'enseignant {teacher.name} a été archivé avec succès !")
    return redirect('teacher_list')


def teacher_archived_list(request):
    """View to display a list of archived teachers."""
    teachers = Teacher.objects.filter(is_active=False)
    return render(request, 'teachers/teacher_archived_list.html', {'teachers': teachers})


def teacher_restore(request, pk):
    """View to restore an archived teacher."""
    teacher = get_object_or_404(Teacher, pk=pk)
    teacher.is_active = True
    teacher.save()
    messages.success(request, f"L'enseignant {teacher.name} a été restauré avec succès !")
    return redirect('teacher_archived_list')