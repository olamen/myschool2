from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from accounting.models import CashRegister

@login_required
def dashs(request):
    """Dashboard for Admins."""
    
    return render(request, 'dash/dashs.html')

@login_required
def dashf(request):
    """Dashboard for Adminf."""

    cash_register = CashRegister.objects.get(user=request.user )
    context = {
        'cash_register' : cash_register
    }

    return render(request, 'dash/dashf.html',context)