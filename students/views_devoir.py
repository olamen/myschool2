# Devoir CRUD

from django.shortcuts import get_object_or_404, redirect, render
from students.forms import CompositionForm, DevoirForm
from students.models import Composition, Devoir

#crude dev
def devoir_list(request):
    devoirs = Devoir.objects.all()
    return render(request, 'students/devoirs/devoir_list.html', {'devoirs': devoirs})

def devoir_create(request):
    if request.method == 'POST':
        form = DevoirForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('devoir_list')
    else:
        form = DevoirForm()
    return render(request, 'students/devoirs/devoir_form.html', {'form': form})

def devoir_update(request, pk):
    devoir = get_object_or_404(Devoir, pk=pk)
    if request.method == 'POST':
        form = DevoirForm(request.POST, instance=devoir)
        if form.is_valid():
            form.save()
            return redirect('devoir_list')
    else:
        form = DevoirForm(instance=devoir)
    return render(request, 'students/devoirs/devoir_form.html', {'form': form})

def devoir_delete(request, pk):
    devoir = get_object_or_404(Devoir, pk=pk)
    if request.method == 'POST':
        devoir.delete()
        return redirect('devoir_list')
    return render(request, 'students/devoirs/devoir_confirm_delete.html', {'devoir': devoir})

# Composition CRUD

def composition_list(request):
    compositions = Composition.objects.all()
    return render(request, 'students/compositions/composition_list.html', {'compositions': compositions})

def composition_create(request):
    if request.method == 'POST':
        form = CompositionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('composition_list')
    else:
        form = CompositionForm()
    return render(request, 'students/compositions/composition_form.html', {'form': form})

def composition_update(request, pk):
    composition = get_object_or_404(Composition, pk=pk)
    if request.method == 'POST':
        form = CompositionForm(request.POST, instance=composition)
        if form.is_valid():
            form.save()
            return redirect('composition_list')
    else:
        form = CompositionForm(instance=composition)
    return render(request, 'students/compositions/composition_form.html', {'form': form})

def composition_delete(request, pk):
    composition = get_object_or_404(Composition, pk=pk)
    if request.method == 'POST':
        composition.delete()
        return redirect('composition_list')
    return render(request, 'students/compositions/composition_confirm_delete.html', {'composition': composition})