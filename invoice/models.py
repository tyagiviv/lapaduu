from django.db import models
from django.contrib.auth.models import User

class Invoice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="invoices", null=True)  # Link to the user
    invoice_number = models.IntegerField(unique=True)  # Store invoice numbers
    client_name = models.CharField(max_length=255)
    client_email = models.EmailField()
    client_address = models.TextField()
    registration_code = models.CharField(max_length=255)
    due_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    mark_as_paid = models.BooleanField(default=False)  # New field to track payment status

    def __str__(self):
        return f"Invoice #{self.invoice_number}"


class Description(models.Model):
    invoice = models.ForeignKey(Invoice, related_name="descriptions", on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.description} - {self.quantity} x {self.price}"