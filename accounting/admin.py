from django.contrib import admin
from .models import CashRegister, ChargeType, Transaction, StudentFee, Fee, Payment, Expense

class CashRegisterAdmin(admin.ModelAdmin):
    list_display = ('date', 'user', 'initial_balance', 'current_balance', 'closed_balance', 'is_open')
    list_filter = ('is_open', 'user')
    search_fields = ('user__username', 'date')

admin.site.register(CashRegister, CashRegisterAdmin)

#//////
admin.site.register(Transaction)
admin.site.register(StudentFee)
admin.site.register(Fee)
admin.site.register(Payment)
admin.site.register(Expense)
admin.site.register(ChargeType)
