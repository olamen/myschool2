from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from accounting.models import CashRegister

@login_required
def dashs(request):
    """Dashboard for Admins."""
    
    return render(request, 'dash/dashs.html')

@login_required
def dashf(request):
    """Dashboard for Adminf."""

    cash_register = CashRegister.objects.filter(user=request.user).first()

    if not cash_register:
        messages.error(request, "Aucun registre de caisse trouvé pour cet utilisateur.")
        return redirect('some_other_page')  # Redirect to a fallback page

    context = {'cash_register': cash_register}
    return render(request, 'dash/dashf.html', context)