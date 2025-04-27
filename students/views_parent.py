from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from Auth.models import RoleChoices
from .models import Parent, Student

def parent_list(request):
    """View to display a list of all parents."""
    parents = Parent.objects.all()
    return render(request, 'students/parent_list.html', {'parents': parents})

def parent_list_card(request):
    """View to display a list of all parents."""
    parents = Parent.objects.all()
    return render(request, 'students/parent_list_card.html', {'parents': parents})

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Parent, Student, CustomUser

def parent_create(request):
    """View to create a new parent and link students."""
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

        # Create a user for the parent
        user = CustomUser.objects.create_user(
            username=nni,
            password='defaultpassword',  # Replace this with a secure password
            first_name=first_name,
            last_name = request.POST.get('last_name'),
            email=email,
        )
        user.is_approved = True
        user.role = RoleChoices.PARENT_OR_STUDENT
        user.save()

        # Create a new parent linked to the user
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
    return render(request, 'students/parent_form.html', {'students': students})


def parent_detail(request, parent_id):
    """View to display details about a specific parent."""
    parent = get_object_or_404(Parent, id=parent_id)
    children = parent.children.all()  # Fetch all linked students

    context = {
        'parent': parent,
        'children': children,
    }
    return render(request, 'students/parent_detail.html', context)