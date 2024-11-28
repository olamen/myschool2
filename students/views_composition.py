from django.shortcuts import render, get_object_or_404, redirect
from .models import Composition

def exam_detail(request, exam_id):
    exam = get_object_or_404(Composition, id=exam_id)
    return render(request, "reporting/exam_detail.html", {"exam": exam})

def edit_exam(request, exam_id):
    exam = get_object_or_404(Composition, id=exam_id)
    if request.method == "POST":
        exam.name = request.POST.get("name")
        exam.exam_date = request.POST.get("exam_date")
        exam.save()
        return redirect("exam_detail", exam_id=exam.id)
    return render(request, "reporting/edit_exam.html", {"exam": exam})