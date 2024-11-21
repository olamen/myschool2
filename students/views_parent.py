from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Parent, Student

def parent_list(request):
    """View to display a list of all parents."""
    parents = Parent.objects.all()
    return render(request, 'students/parent_list.html', {'parents': parents})

def parent_create(request):
    """View to create a new parent and link students."""
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        children_ids = request.POST.getlist('children')  # List of student IDs
        photo = request.FILES.get('photo')  # Handle uploaded photo

        # Create a new parent
        parent = Parent.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            address=address,
            photo=photo  # Save the uploaded photo
        )
        parent.children.set(Student.objects.filter(id__in=children_ids))
        parent.save()

        messages.success(request, f"Parent {parent.first_name} {parent.last_name} created successfully!")
        return redirect('parent_list')

    # Get only students who are not already associated with a parent
    students = Student.objects.exclude(parents__isnull=False)

    # allow student to have two parent
    #students = Student.objects.annotate(parent_count=Count('parents')).filter(parent_count__lt=2)
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