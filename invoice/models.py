from django.db import models

class Invoice(models.Model):
    invoice_number = models.IntegerField(unique=True)  # Store invoice numbers
    client_name = models.CharField(max_length=255)
    client_email = models.EmailField()
    client_address = models.TextField()
    registration_code = models.CharField(max_length=255)
    due_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice #{self.invoice_number}"
