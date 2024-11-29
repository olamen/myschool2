from datetime import date
import uuid
from django.db import models
from Auth.models import CustomUser
from students.models import Classe, Parent, Student

class Expense(models.Model):
    """
    Model for tracking school expenses (e.g., utilities, maintenance, salaries).
    """
    name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.TextField(null=True, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)  # User who processed the payment

    def __str__(self):
        return f"{self.name} - {self.amount}"


class Fee(models.Model):
    """
    Model for tracking school fees (monthly, yearly) assigned to a student or parent1.
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fees')
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    paid = models.BooleanField(default=False)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)  # User who processed the payment
    def __str__(self):
        return f"Fee for {self.student.first_name} {self.student.last_name} - {'Paid' if self.paid else 'Unpaid'}"

class ParentAccount(models.Model):
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name='accounts')  # Link to Parent model
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE, related_name='parent_accounts')  # Link to Classe model
    user = models.ForeignKey('Auth.CustomUser', on_delete=models.SET_NULL, null=True, blank=True)  # User who processed the payment

    def get_total_fees(self):
        """
        Calculate the total fees for all students in the parent's class.
        """
        total_fees = 0
        for child in self.parent.children.all():
            if child.student_class == self.classe:
                discount = 0.2 if child.has_discount else 0
                fee = child.student_class.monthly_salary_fee
                total_fees += fee - (fee * discount)
        return total_fees

    def __str__(self):
        return f"ParentAccount for {self.parent.first_name} {self.parent.last_name} in {self.classe.name}"

class Payment(models.Model):
    """
    Model for recording payments made by a student or a parent.
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='individual_payments', null=True, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)  # User who processed the payment
    parent_account = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    method = models.CharField(max_length=50, choices=[('Cash', 'Cash'), ('Bank', 'Bank Transfer')], default='Cash')

    def __str__(self):
        if self.student:
            return f"Payment by {self.student.first_name} {self.student.last_name} - {self.amount_paid}"
        elif self.parent_account:
            return f"Payment by {self.parent_account.parent_name} - {self.amount_paid}"
        else:
            return f"Payment of {self.amount_paid}"
        
MONTH_CHOICES = [
    (1, "January"),
    (2, "February"),
    (3, "March"),
    (4, "April"),
    (5, "May"),
    (6, "June"),
    (7, "July"),
    (8, "August"),
    (9, "September"),
    (10, "October"),
    (11, "November"),
    (12, "December"),
]

class MonthPayment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='monthly_payments')
    month = models.PositiveSmallIntegerField(choices=MONTH_CHOICES)  # Month (e.g., 1 for January)
    year = models.PositiveIntegerField(default=date.today().year)  # Year for the payment
    amount = models.DecimalField(max_digits=8, decimal_places=2)  # Amount for the month
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)  # User who processed the payment
    status = models.CharField(
        max_length=20,
        choices=[
            ('Paid', 'Paid'),
            ('Pending', 'Pending'),
            ('Skipped', 'Skipped'),
        ],
        default='Pending'
    )
    payment_date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'month', 'year')  # Ensure no duplicate months for the same student

    def __str__(self):
        return f"{self.student.first_name} {self.student.last_name} - {MONTH_CHOICES[self.month - 1][1]} {self.year}"
    

class Transaction(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="transactions")
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)  # User who processed the payment
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    months_paid = models.TextField()  # Store the months paid in JSON format or comma-separated
    receipt_number = models.CharField(max_length=20, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            self.receipt_number = str(uuid.uuid4().hex[:20]).upper()  # Generate unique receipt number
        super(Transaction, self).save(*args, **kwargs)

    def __str__(self):
        return f"Transaction for {self.student.first_name} {self.student.last_name} - {self.total_amount} on {self.payment_date}"