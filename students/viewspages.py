from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def dashs(request):
    """Dashboard for Admins."""
    return render(request, 'dash/dashs.html')

@login_required
def dashf(request):
    """Dashboard for Adminf."""
    return render(request, 'dash/dashf.html')