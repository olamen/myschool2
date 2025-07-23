from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from Auth.models import CustomUser, RoleChoices
from .models import Parent, Student
from django.contrib.auth.decorators import login_required


def parent_list(request):
    """View to display a list of all parents."""
    parents = Parent.objects.all()
    return render(request, 'students/parent_list.html', {'parents': parents})

def parent_list_card(request):
    """View to display a list of all parents."""
    parents = Parent.objects.all()
    return render(request, 'students/parent_list_card.html', {'parents': parents})


@login_required
def parent_create_or_update(request, parent_id=None): 
    """View to create or update a parent and link students."""
    if parent_id:
        parent = get_object_or_404(Parent, id=parent_id)
        user = parent.user
        parent_children_ids = list(parent.children.all().values_list('id', flat=True))
    else:
        parent = None
        user = None
        parent_children_ids = []

    if request.method == 'POST':
        # Collect form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        nni = request.POST.get('nni')
        address = request.POST.get('address')
        children_ids = request.POST.getlist('children')  # List of student IDs
        photo = request.FILES.get('photo')  # Handle uploaded photo

        if parent:
            # Update existing user and parent
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.username = nni
            user.save()

            parent.first_name = first_name
            parent.last_name = last_name
            parent.nni = nni
            parent.email = email
            parent.phone_number = phone_number
            parent.address = address
            if photo:
                parent.photo = photo
            parent.children.set(Student.objects.filter(id__in=children_ids))
            parent.save()

            messages.success(request, f"Parent {parent.first_name} {parent.last_name} updated successfully!")
        else:
            # Create a new user and parent
            user = CustomUser.objects.create_user(
                username=nni,
                password='defaultpassword',  # Replace this with a secure password
                first_name=first_name,
                last_name=last_name,
                email=email,
            )
            user.is_approved = True
            user.role = RoleChoices.PARENT_OR_STUDENT
            user.save()

            parent = Parent.objects.create(
                first_name=first_name,
                last_name=last_name,
                nni=nni,
                email=email,
                phone_number=phone_number,
                address=address,
                photo=photo,
                user=user  # Link the parent to the created user
            )
            parent.children.set(Student.objects.filter(id__in=children_ids))
            parent.save()

            messages.success(request, f"Parent {parent.first_name} {parent.last_name} created successfully!")

        return redirect('parent_list')

    # Get only students who are not already associated with a parent
    students = Student.objects.exclude(parents__isnull=False)
    context = {
        'parent': parent,
        'students': students,
        'parent_children_ids': parent_children_ids,

    }
    return render(request, 'students/parent_form.html', context)


def parent_detail(request, parent_id):
    """View to display details about a specific parent."""
    parent = get_object_or_404(Parent, id=parent_id)
    children = parent.children.all()  # Fetch all linked students

    context = {
        'parent': parent,
        'children': children,
    }
    return render(request, 'students/parent_detail.html', context)

@login_required
def delete_parent(request, parent_id):
    """View to delete a parent."""
    parent = get_object_or_404(Parent, id=parent_id)
    if request.method == 'POST':
        parent.delete()
        messages.success(request, f"Parent {parent.first_name} {parent.last_name} deleted successfully!")
        return redirect('parent_list')
    return render(request, 'students/confirm_delete.html', {'object': parent})