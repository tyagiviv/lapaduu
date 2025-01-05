from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .utils import get_next_invoice_number
from .models import Invoice
from datetime import datetime
import os
import json
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table


@login_required
def generate_invoice(request):
    # Get the next invoice number
    invoice_number = get_next_invoice_number()

    if request.method == 'POST':
        try:
            # Parse the incoming JSON data
            data = json.loads(request.body)

            # Access the fields from the parsed data
            client_email = data.get('clientEmail')
            invoice_date = data.get('invoiceDate')
            client_name = data.get('clientName')
            client_address = data.get('clientAddress')
            registration_code = data.get('registrationCode')
            due_date = data.get('dueDate')

            descriptions = data.get('descriptions', [])
            quantities = data.get('quantities', [])
            prices = data.get('prices', [])
            discounts = data.get('discounts', [])
            totals = data.get('totals', [])

            if not client_email or not invoice_date or not client_name:
                return JsonResponse({'error': 'Missing required fields!'}, status=400)

            if not descriptions or not quantities or not prices or not discounts or not totals:
                return JsonResponse({'error': 'Missing description data!'}, status=400)

            invoice_number = get_next_invoice_number()
            total_amount = sum([float(total) for total in totals])

            invoice = Invoice.objects.create(
                invoice_number=invoice_number,
                client_name=client_name,
                client_email=client_email,
                client_address=client_address,
                registration_code=registration_code,
                due_date=due_date,
                total_amount=total_amount
            )

            # Generate the PDF
            today = datetime.now().strftime("%Y-%m-%d")
            folder_path = os.path.join(os.getcwd(), 'invoices', today)
            os.makedirs(folder_path, exist_ok=True)
            pdf_filename = os.path.join(folder_path, f"Invoice_{invoice_number}.pdf")

            doc = SimpleDocTemplate(pdf_filename, pagesize=letter)
            elements = []
            elements.append(Paragraph(f"Invoice #{invoice_number}", getSampleStyleSheet()['Title']))

            # Prepare the table data
            table_data = [['Description', 'Quantity', 'Price', 'Discount', 'Total']]  # Table headers
            for i in range(len(descriptions)):
                row = [
                    descriptions[i],
                    quantities[i],
                    prices[i],
                ]
                # Include the discount only if it's non-zero
                discount_value = discounts[i]
                if float(discount_value) > 0:
                    row.append(f"{discount_value}%")
                else:
                    row.append("")  # Leave the discount cell blank

                row.append(totals[i])
                table_data.append(row)

            table = Table(table_data)
            elements.append(table)
            elements.append(Spacer(1, 12))
            elements.append(Paragraph(f"Total Amount: {total_amount:.2f} EUR", getSampleStyleSheet()['Normal']))

            doc.build(elements)

            return JsonResponse({'success': True, 'filename': pdf_filename})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    else:
        return render(request, 'generator.html')
