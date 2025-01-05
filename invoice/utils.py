from .models import Invoice

def get_next_invoice_number():
    last_invoice = Invoice.objects.last()
    return last_invoice.invoice_number + 1 if last_invoice else 1
