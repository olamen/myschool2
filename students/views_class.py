from django.contrib import messages
from django.db import IntegrityError
from .forms import ClasseForm
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required


from .models import Classe


def class_archive(request, class_id):
    """
    Archive a class by setting is_active to False.
    """
    cls = get_object_or_404(Classe, id=class_id)
    cls.is_active = False
    cls.save()
    messages.success(request, f"La classe '{cls.name}' a été archivée avec succès.")
    return redirect('class_list')


def class_archived_list(request):
    """
    View to list all archived classes.
    """
    # Fetch all archived classes
    archived_classes = Classe.objects.filter(is_active=False)
    return render(request, 'classes/class_archived_list.html', {'classes': archived_classes})



@login_required
def create_or_update_classe(request, classe_id=None):
    if classe_id:
        # Mise à jour
        classe = get_object_or_404(Classe, id=classe_id)
        if request.method == 'POST':
            form = ClasseForm(request.POST, instance=classe)
            if form.is_valid():
                form.save()
                return redirect('list_classes')
        else:
            form = ClasseForm(instance=classe)
    else:
        # Création
        classe = None
        if request.method == 'POST':
            form = ClasseForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('list_classes')
        else:
            form = ClasseForm()
    
    return render(request, 'classes/create_or_update_classe.html', {'form': form, 'classe': classe})

@login_required
def list_classes(request):
    classes = Classe.objects.all()
    return render(request, 'classes/list_classes.html', {'classes': classes})
