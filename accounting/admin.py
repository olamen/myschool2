from django.contrib import admin
from .models import CashRegister, Transaction, StudentFee, Fee, Payment, Expense

admin.site.register(CashRegister)
admin.site.register(Transaction)
admin.site.register(StudentFee)
admin.site.register(Fee)
admin.site.register(Payment)
admin.site.register(Expense)
