from django.contrib import messages
from django.db import IntegrityError
from django.shortcuts import redirect, render, get_object_or_404

from .models import Class

def class_create(request):
    """
    View to create a new class.
    """
    if request.method == 'POST':
        name = request.POST.get('name')
        monthly_salary_fee = request.POST.get('monthly_salary_fee')

        try:
            # Try to create the class
            new_class = Class.objects.create(name=name, monthly_salary_fee=monthly_salary_fee)
            messages.success(request, f"Classe '{new_class.name}' créée avec succès !")
            return redirect('class_list')
        except IntegrityError:
            # Handle duplicate class name error
            messages.error(request, f"Une classe avec le nom '{name}' existe déjà. Veuillez choisir un autre nom.")

    return render(request, 'classes/class_form.html')

def class_list(request):
    """
    View to list all active classes.
    """
    # Fetch all active classes
    classes = Class.objects.filter(is_active=True)
    return render(request, 'classes/class_list.html', {'classes': classes})

def class_archive(request, class_id):
    """
    Archive a class by setting is_active to False.
    """
    cls = get_object_or_404(Class, id=class_id)
    cls.is_active = False
    cls.save()
    messages.success(request, f"La classe '{cls.name}' a été archivée avec succès.")
    return redirect('class_list')

def class_update(request, class_id):
    """
    View to update an existing class.
    """
    cls = get_object_or_404(Class, id=class_id)  # Fetch the class to update

    if request.method == 'POST':
        # Get data from the form
        cls.name = request.POST.get('name')
        cls.monthly_salary_fee = request.POST.get('monthly_salary_fee')

        # Save the updated class
        cls.save()
        messages.success(request, f"La classe '{cls.name}' a été mise à jour avec succès.")
        return redirect('class_list')  # Redirect to the class list

    # Render the form with existing class data
    return render(request, 'classes/class_form.html', {'cls': cls})

def class_archived_list(request):
    """
    View to list all archived classes.
    """
    # Fetch all archived classes
    archived_classes = Class.objects.filter(is_active=False)
    return render(request, 'classes/class_archived_list.html', {'classes': archived_classes})