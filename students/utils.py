from django.db import transaction
from students.models import Teacher
import random

@transaction.atomic
def populate_nni_for_existing_records():
    """
    Populate the `nni` field for existing Teacher records if empty.
    NNI will be a 10-digit unique number.
    """
    teachers = Teacher.objects.filter(nni__isnull=True)  # Or use `nni=''` if empty strings are used
    existing_nnis = set(Teacher.objects.exclude(nni__isnull=True).values_list('nni', flat=True))

    for teacher in teachers:
        nni = None
        while not nni or nni in existing_nnis:
            nni = ''.join(random.choices('0123456789', k=10))
        teacher.nni = nni
        teacher.save()
        existing_nnis.add(nni)  # Update the set to avoid duplicates

    print(f"{teachers.count()} records updated.")
