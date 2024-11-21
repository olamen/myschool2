from django.contrib import admin
from .models import Expense, Fee, MonthPayment, ParentAccount, Payment

admin.site.register(Expense)
admin.site.register(Fee)
admin.site.register(ParentAccount)
admin.site.register(Payment)
admin.site.register(MonthPayment)