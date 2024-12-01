from datetime import date
from django.conf import settings
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from students.models import Classe, Parent, Student, Teacher  # Modèles existants
from django.utils.timezone import now


CustomUser = get_user_model()

class Fee(models.Model):
    """
    Modèle pour suivre les frais scolaires assignés à un étudiant.
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='feesstudent')  # Étudiant concerné
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)  # Montant dû
    due_date = models.DateField()  # Date d'échéance du paiement
    paid = models.BooleanField(default=False)  # Indique si le frais a été payé
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)  # Utilisateur ayant enregistré ou modifié ce frais

    def __str__(self):
        return f"Frais pour {self.student.first_name} {self.student.last_name} - {'Payé' if self.paid else 'Non Payé'}"

    class Meta:
        ordering = ['-due_date']  # Trie par date d'échéance décroissante
        verbose_name = "Frais étudiant"
        verbose_name_plural = "Frais étudiants"

    def is_due(self):
        """
        Vérifie si le paiement est en retard.
        """
        return not self.paid and self.due_date < date.today()
    
class CashRegister(models.Model):
    """
    Modèle pour gérer l'état de la caisse.
    """
    initial_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    current_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Default added
    closed_balance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    date = models.DateField(auto_now_add=True)
    is_open = models.BooleanField(default=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"Caisse du {self.date} - {self.user}"

    def open_register(self, opening_balance):
        """
        Ouvrir la caisse avec un solde d'ouverture.
        """
        if self.is_open:
            raise ValueError("La caisse est déjà ouverte.")
        self.opening_balance = opening_balance
        self.current_balance = opening_balance  # Initialise le solde actuel avec le solde d'ouverture
        self.is_open = True
        self.save()

    def close_register(self, closing_balance):
        """
        Fermer la caisse et enregistrer le solde de fermeture.
        """
        if not self.is_open:
            raise ValueError("La caisse est déjà fermée.")
        self.closing_balance = closing_balance
        self.is_open = False
        self.save()

    def save(self, *args, **kwargs):
        if self.is_open:
            # Close other open cash registers
            CashRegister.objects.filter(is_open=True).update(is_open=False)
        super().save(*args, **kwargs)

    def update_current_balance(self, amount, transaction_type):
        """
        Mettre à jour le solde actuel de la caisse.
        """
        if not self.is_open:
            raise ValueError("Impossible de mettre à jour le solde : la caisse est fermée.")
        if transaction_type == "income":
            self.current_balance += amount
        elif transaction_type == "expense":
            self.current_balance -= amount
        else:
            raise ValueError("Type de transaction invalide.")
        self.save()


class Transaction(models.Model):
    cash_register = models.ForeignKey(
        CashRegister, 
        on_delete=models.CASCADE, 
        related_name="transactions"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(
        max_length=20,
        choices=[
            ('Credit', 'Credite'),  # Entrée d'argent
            ('Debit', 'Debite')    # Sortie d'argent
        ],
        default='Credit'
    )
    description = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name="transactions"
    )

    def __str__(self):
        return f"{self.type} - {self.amount} on {self.date}"

# Signal pour mettre à jour la caisse après une transaction
@receiver(post_save, sender=Transaction)
def update_cash_register(sender, instance, **kwargs):
    """
    Met à jour le solde actuel de la caisse après chaque transaction.
    """
    if instance.type == 'Credit':
        instance.cash_register.current_balance += instance.amount
    elif instance.type == 'Debit':
        instance.cash_register.current_balance -= instance.amount
    instance.cash_register.save()


class StudentFee(models.Model):
    """
    Paiements pour les frais scolaires des élèves.
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="fees")
    amount = models.DecimalField(_("Montant"), max_digits=10, decimal_places=2)
    due_date = models.DateField(_("Date limite"))
    is_paid = models.BooleanField(_("Payé"), default=False)
    payment_date = models.DateField(_("Date de paiement"), null=True, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="transactionsstudentuser")
    cash_register = models.ForeignKey(CashRegister, on_delete=models.CASCADE, related_name="student_fees")

    def save(self, *args, **kwargs):
        """
        Enregistre le paiement et crée une transaction.
        """
        if self.is_paid and self.payment_date:
            # Crée une transaction pour ce paiement
            transaction = Transaction(
                amount=self.amount,
                transaction_type="income",
                description=f"Paiement des frais pour {self.student.first_name} {self.student.last_name}",
                user=self.cash_register.user,
                cash_register=self.cash_register,
            )
            transaction.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Frais pour {self.student.first_name} {self.student.last_name} - {'Payé' if self.is_paid else 'Non payé'}"
    


class Expense(models.Model):
    """
    Modèle pour les dépenses associées à une caisse.
    """
    CATEGORY_CHOICES = [
        ('maintenance', _('Maintenance')),
        ('utilities', _('Services publics')),
        ('salary', _('Salaire')),
        ('supplies', _('Fournitures')),
        ('other', _('Autre')),
    ]

    cash_register = models.ForeignKey(
        CashRegister, 
        on_delete=models.CASCADE, 
        related_name="expenses",
        verbose_name=_("Caisse")
    )
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name=_("Utilisateur")
    )
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='other',
        verbose_name=_("Catégorie")
    )
    description = models.TextField(
        verbose_name=_("Description"),
        blank=True, 
        null=True
    )
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name=_("Montant")
    )
    date = models.DateField(
        auto_now_add=True,
        verbose_name=_("Date")
    )

    def __str__(self):
        return f"{self.get_category_display()} - {self.amount} ({self.date})"
    
class Payment(models.Model):
    """
    Modèle pour enregistrer les paiements effectués par un étudiant ou un parent.
    """
    PAYMENT_METHOD_CHOICES = [
        ('cash', _('Espèces')),
        ('bank', _('Virement bancaire')),
        ('check', _('Chèque')),
        ('other', _('Autre')),
    ]

    cash_register = models.ForeignKey(
        CashRegister,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name=_("Caisse")
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
        verbose_name=_("Étudiant")
    )
    parent = models.ForeignKey(
        Parent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
        verbose_name=_("Parent")
    )
    classe = models.ForeignKey(
        Classe,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="class_payments",
        verbose_name=_("Classe")
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Utilisateur")
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Montant")
    )
    method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='cash',
        verbose_name=_("Méthode de paiement")
    )
    date = models.DateTimeField(
        default=now,
        verbose_name=_("Date")
    )
    receipt_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("Numéro de reçu"),
        blank=True
    )
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Notes")
    )

    def save(self, *args, **kwargs):
        """
        Méthode personnalisée pour mettre à jour le solde de la caisse et générer un numéro de reçu.
        """
        is_new_payment = not self.pk  # Vérifie si c'est une nouvelle instance
        if not self.receipt_number:
            self.receipt_number = f"PAY-{now().strftime('%Y%m%d%H%M%S')}"
        super().save(*args, **kwargs)  # Sauvegarde l'instance

        # Mettre à jour la caisse uniquement si c'est un nouveau paiement
        if is_new_payment:
            self.cash_register.current_balance += self.amount
            self.cash_register.save()

    def __str__(self):
        if self.student:
            return f"Paiement de {self.student.first_name} {self.student.last_name} - {self.amount} MRU"
        elif self.parent:
            return f"Paiement de {self.parent.first_name} {self.parent.last_name} - {self.amount} MRU"
        elif self.classe:
            return f"Paiement pour la classe {self.classe.name} - {self.amount} MRU"
        return f"Paiement de {self.amount} MRU"