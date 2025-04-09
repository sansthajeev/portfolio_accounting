from django.db import models

ACCOUNT_TYPES = [
    ('asset', 'Asset'),
    ('liability', 'Liability'),
    ('equity', 'Equity'),
    ('income', 'Income'),
    ('expense', 'Expense'),
]

class Account(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.code} - {self.name}"
    
class JournalType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    prefix = models.CharField(max_length=10, help_text="Prefix for auto-generated serials (e.g., INV, CASH, BANK)")

    def __str__(self):
        return self.name


class Transaction(models.Model):
    description = models.CharField(max_length=255)
    date = models.DateField(auto_now_add=True)
    journal = models.ForeignKey(JournalType, on_delete=models.PROTECT)
    serial_number = models.CharField(max_length=50, blank=True, null=True)  # auto-generated

    def save(self, *args, **kwargs):
        if not self.serial_number:
            last_tx = Transaction.objects.filter(journal=self.journal).order_by('-id').first()
            count = 1 if not last_tx else int(last_tx.serial_number.split('-')[-1]) + 1
            self.serial_number = f"{self.journal.prefix}-{count:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.serial_number} - {self.description}"


class Entry(models.Model):
    transaction = models.ForeignKey(Transaction, related_name='entries', on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    entry_type = models.CharField(max_length=6, choices=[('debit', 'Debit'), ('credit', 'Credit')])


class Portfolio(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Investment(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='investments')
    asset_name = models.CharField(max_length=100)
    asset_type = models.CharField(max_length=50)
    symbol = models.CharField(max_length=20, null=True, default="NA")
    purchase_date = models.DateField()
    units = models.PositiveIntegerField()
    face_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    amount_invested = models.DecimalField(max_digits=12, decimal_places=2)
    current_value = models.DecimalField(max_digits=12, decimal_places=2)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='investment', null=True, blank=True)


    def __str__(self):
        return self.asset_name


class Shareholder(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    account = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='shareholder')

    def __str__(self):
        return self.name
