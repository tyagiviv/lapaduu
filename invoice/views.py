from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .utils import get_next_invoice_number
from .models import Invoice, Description
from datetime import datetime
import os
import json
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table

@login_required
def generate_invoice(request):
    # Get the next invoice number at the beginning
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

            # Create the invoice with the generated invoice number
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

            # Create Description entries for the invoice
            for i in range(len(descriptions)):
                Description.objects.create(
                    invoice=invoice,
                    description=descriptions[i],
                    quantity=quantities[i],
                    price=prices[i],
                    discount=discounts[i],
                    total_amount=totals[i]
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

            # Return the next invoice number in the response (after the invoice creation)
            return JsonResponse({
                'success': True,
                'filename': pdf_filename,
                'next_invoice_number': invoice_number + 1  # Increment the number for the next invoice
            })

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            # Log the exception for debugging purposes
            print(f"Error: {e}")
            return JsonResponse({'error': 'An error occurred while processing your request'}, status=500)
    else:
        # Pass the current invoice number to the template
        return render(request, 'generator.html', {'invoice_number': invoice_number})


def get_next_invoice_number_view(request):
    try:
        next_invoice_number = get_next_invoice_number()  # Call the utility function
        return JsonResponse({'success': True, 'next_invoice_number': next_invoice_number})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
