from django.shortcuts import get_object_or_404, redirect, render
from students.forms import TrimestreForm
from django.contrib import messages
from students.models import Trimestre


def trimestre_list(request):
    trimestres = Trimestre.objects.all()
    return render(request, 'students/trimestres/trimestre_list.html', {'trimestres': trimestres})

def trimestre_create(request):
    if request.method == 'POST':
        form = TrimestreForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"Trimestre créé avec succès !")
            return redirect('trimestre_list')
    else:
        form = TrimestreForm()
    return render(request, 'students/trimestres/trimestre_form.html', {'form': form})

def trimestre_update(request, pk):
    trimestre = get_object_or_404(Trimestre, pk=pk)
    if request.method == 'POST':
        form = TrimestreForm(request.POST, instance=trimestre)
        if form.is_valid():
            form.save()
            return redirect('trimestre_list')
    else:
        form = TrimestreForm(instance=trimestre)
    return render(request, 'students/trimestres/trimestre_form.html', {'form': form})

def trimestre_delete(request, pk):
    trimestre = get_object_or_404(Trimestre, pk=pk)
    if request.method == 'POST':
        trimestre.delete()
        messages.success(request, f"Trimestre a été supprimer avec succès !")
        return redirect('trimestre_list')
    return render(request, 'students/trimestres/trimestre_confirm_delete.html', {'trimestre': trimestre})