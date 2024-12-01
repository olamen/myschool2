from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from students.forms import TeacherForm
from .models import Teacher

def teacher_list(request):
    teachers = Teacher.objects.filter(Active=False)
    return render(request, "teachers/teacher_list.html", {"teachers": teachers})

def teacher_create(request):
    if request.method == "POST":
        form = TeacherForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Teacher added successfully!")
            return redirect("teacher_list")
    else:
        form = TeacherForm()
    return render(request, "teachers/teacher_form.html", {"form": form})

def teacher_update(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == "POST":
        form = TeacherForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, "Teacher updated successfully!")
            return redirect("teacher_list")
    else:
        form = TeacherForm(instance=teacher)
    return render(request, "teachers/teacher_form.html", {"form": form})

def teacher_delete(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == "POST":
        teacher.delete()
        messages.success(request, "Teacher deleted successfully!")
        return redirect("teacher_list")
    return render(request, "teachers/teacher_confirm_delete.html", {"teacher": teacher})

#Real-Time NNI Verification Using AJAX
def check_nni_existence(request):
    nni = request.GET.get('nni', None)
    if nni:
        exists = Teacher.objects.filter(nni=nni).exists()
        return JsonResponse({'exists': exists})
    return JsonResponse({'exists': False})