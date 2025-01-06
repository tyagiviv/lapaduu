from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .utils import get_next_invoice_number, send_invoice
from .models import Invoice, Description
from datetime import datetime
import os
import json
from django.conf import settings
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import PageTemplate, Frame


# Footer function
def add_footer(canvas, _doc):
    canvas.saveState()
    width, height = letter
    line_position = inch  # Set line position from the bottom

    # Draw a solid line above the footer
    canvas.setLineWidth(1)
    canvas.line(0.75 * inch, line_position + 0.2 * inch, width - 0.75 * inch, line_position + 0.2 * inch)

    # Set font for the footer
    canvas.setFont("Helvetica", 9)

    # Footer contents
    footer_part1 = [
        ("LapaDuu OÜ", 0.75 * inch),  # Name
        ("Reg.nr 14842122", 3.2 * inch),  # Registration number
        ("Swedbank: EE122200221072678443", 5.5 * inch)  # Bank info
    ]

    footer_part2 = [
        ("Pärnu mnt 129b-14, Tallinn", 0.75 * inch),  # Address
        ("Tel: +372 53702287", 3.2 * inch),  # Phone number
    ]

    footer_part3 = [
        ("Harjumaa, 11314", 0.75 * inch),  # County and postal code
        ("email: lapaduu@lapaduu.ee", 3.2 * inch)  # Email
    ]

    # Draw footer contents
    for text, x_position in footer_part1:
        canvas.drawString(x_position, line_position - 10, text)

    for text, x_position in footer_part2:
        canvas.drawString(x_position, line_position - 25, text)

    for text, x_position in footer_part3:
        canvas.drawString(x_position, line_position - 40, text)

    # Set color to blue for the email link
    canvas.setFillColor(colors.blue)

    # Draw the email text
    email_x = 3.2 * inch  # Same position as the email text
    email_y = line_position - 40  # Corresponding y position
    canvas.drawString(email_x, email_y, "email: lapaduu@lapaduu.ee")

    # Draw an underline for the email
    email_text_width = canvas.stringWidth("email: lapaduu@lapaduu.ee", "Helvetica", 9)
    canvas.setLineWidth(0.5)  # Set line width for underline
    canvas.line(email_x, email_y - 2, email_x + email_text_width, email_y - 2)  # Draw the underline

    # Create a clickable email link
    canvas.linkURL("mailto:lapaduu@lapaduu.ee", (email_x, email_y - 5, email_x + 100, email_y + 5), relative=1)

    # Restore the canvas state
    canvas.restoreState()


@login_required
def generate_invoice(request):
    # Get the next invoice number at the beginning
    invoice_number = get_next_invoice_number()

    if request.method == 'POST':
        try:
            # Parse the incoming JSON data
            data = json.loads(request.body)

            # Access the fields from the parsed data
            client_email = data.get('clientEmail').strip()
            invoice_date = data.get('invoiceDate')
            client_name = data.get('clientName').strip()
            client_address = data.get('clientAddress').strip()
            registration_code = data.get('registrationCode').strip()
            due_date = data.get('dueDate')
            mark_as_paid = data.get('markAsPaid', False)  # Add the mark_as_paid field

            descriptions = data.get('descriptions', [])
            quantities = data.get('quantities', [])
            prices = data.get('prices', [])
            discounts = data.get('discounts', [])
            totals = data.get('totals', [])

            # If client name is empty, set default value 'ERAISIK'
            if not client_name:
                client_name = 'ERAISIK'

            # If all client fields are empty, set default values for other fields
            if not client_email:
                client_email = ' '  # You can customize this
            if not client_address:
                client_address = ' '  # You can customize this
            if not registration_code:
                registration_code = ' '  # Optional, can be kept empty if needed


            if not invoice_date or not client_name:
                missing_fields = []
                if not invoice_date:
                    missing_fields.append('Invoice date')
                if not client_name:
                    missing_fields.append('Client name')

                return JsonResponse({'error': f'Missing required '
                                              f'fields: {", ".join(missing_fields)}!'}, status=400)


            if not descriptions or not quantities or not prices or not discounts or not totals:
                missing_data = []
                if not descriptions:
                    missing_data.append('Descriptions')
                if not quantities:
                    missing_data.append('Quantities')
                if not prices:
                    missing_data.append('Prices')
                if not discounts:
                    missing_data.append('Discounts')
                if not totals:
                    missing_data.append('Totals')

                return JsonResponse({'error': f'Missing data: {", ".join(missing_data)}!'}, status=400)


            # Create the invoice with the generated invoice number
            total_amount = sum([float(total) for total in totals])

            invoice = Invoice.objects.create(
                user=request.user,  # Associate the logged-in user with the invoice
                invoice_number=invoice_number,
                client_name=client_name,
                client_email=client_email,
                client_address=client_address,
                registration_code=registration_code,
                due_date=due_date,
                total_amount=total_amount,
                mark_as_paid=mark_as_paid
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

            # Create a PageTemplate that includes the footer
            frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
            template = PageTemplate(id='footer', frames=frame, onPage=add_footer)
            doc.addPageTemplates([template])

            elements = []

            logo_path = os.path.join(settings.BASE_DIR, 'invoice', 'static', 'logo.png')
            print(f"Resolved logo path: {logo_path}")

            # Verify the logo file exists
            if not os.path.exists(logo_path):
                return JsonResponse({'error': 'Logo file not found!'}, status=500)

            logo = Image(logo_path)
            logo.drawWidth = 100
            logo.drawHeight = 85

            # Prepare the table data
            title_table = Table([[logo, Paragraph("LapaDuu OÜ", getSampleStyleSheet()['Title'])]],
                                colWidths=[100, None])
            title_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'LEFT')
            ]))
            elements.append(title_table)

            left_text = f"Klient: {client_name}\nAddress: {client_address}\nReg kood: {registration_code}"
            right_text = (f"Arve nr: {invoice_number}\nArve kuupäev: {invoice_date}"
                          f"\nMakse tähtaeg: {due_date}\nViivis: 0,15% päevas")

            left_table = Table([[Paragraph(line, getSampleStyleSheet()['Normal'])] for line in left_text.split('\n')])
            left_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]))

            right_table = Table([[Paragraph(line, getSampleStyleSheet()['Normal'])] for line in right_text.split('\n')])
            right_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]))

            client_details = Table([[left_table, right_table]], colWidths=[250, 250])
            elements.append(client_details)

            elements.append(Spacer(1, 20))

            # Check if the invoice is marked as paid
            print(f"Mark as Paid: {mark_as_paid}")  # Debugging line
            if mark_as_paid:
                # Use your custom style for the "Paid" label
                paid_label_style = getSampleStyleSheet()['Title']
                paid_label_style.textColor = colors.green  # Set text color to green
                paid_label = Paragraph("<b>Paid</b>", paid_label_style)
                elements.append(paid_label)



            discounts_present = any(float(d) > 0 for d in discounts)
            if discounts_present:
                data = [['Teenus/kaup', 'Ühiku hind', 'Kogus/h', 'Discount (%)', 'Summa']]
            else:
                data = [['Teenus/kaup', 'Ühiku hind', 'Kogus/h', 'Summa']]

            for i in range(len(descriptions)):
                row = [
                    Paragraph(descriptions[i], getSampleStyleSheet()['Normal']),
                    f"{float(prices[i]):.2f}",
                    quantities[i],
                ]
                if discounts_present:
                    row.append(f"{discounts[i]}%" if discounts[i] else '')
                row.append(f"{float(totals[i]):.2f}")
                data.append(row)

            table = Table(data, colWidths=[200, 100, 100, 100, 100] if discounts_present else [200, 100, 100, 100])
            table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]))
            elements.append(table)

            elements.append(Spacer(1, 20))

            right_align_style = ParagraphStyle(name='RightAlign', parent=getSampleStyleSheet()['Normal'],
                                               alignment=TA_RIGHT)
            elements.append(Paragraph("Käibemaks: Ei ole KM kohuslane", right_align_style))
            elements.append(Paragraph(f"<b>Arve summa kokku (EUR): {total_amount:.2f}</b>", right_align_style))

            left_align_style = ParagraphStyle(name='LeftAlign', parent=getSampleStyleSheet()['Normal'],
                                              alignment=TA_LEFT)
            elements.append(Spacer(1, 100))
            elements.append(Paragraph("Palume arve tasumisel märkida selgitusse arve number.", left_align_style))
            elements.append(Paragraph("LapaDuu OÜ ei ole käibemaksukohuslane.", left_align_style))

            doc.build(elements)

            # Send the email after the invoice is generated
            email_sent = False  # Default value

            if client_email and client_email.strip():  # Ensure the email is not empty or invalid
                email_sent = send_invoice(client_email, pdf_filename)

            # Prepare email status message only if an email was sent or failed
            email_status = None
            if email_sent:
                email_status = 'Email sent successfully!'
            elif client_email.strip():  # Only provide this message if email is provided
                email_status = 'Failed to send email. Maybe wrong email address'


            # Return the next invoice number in the response (after the invoice creation)
            response_data = {
                'success': True,
                'filename': pdf_filename,
                'next_invoice_number': invoice_number + 1,  # Increment the number for the next invoice

            }

            # Include email_status in the response only if it is set
            if email_status:
                response_data['email_status'] = email_status

            return JsonResponse(response_data)

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
