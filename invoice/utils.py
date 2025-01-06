import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import configparser
from .models import Invoice

def get_next_invoice_number():
    last_invoice = Invoice.objects.last()
    return last_invoice.invoice_number + 1 if last_invoice else 1

def send_invoice(email_recipient, invoice_file_path):
    # Check if email_recipient is empty or invalid
    if not email_recipient or email_recipient.strip() == '':
        print("Error: No recipient email provided.")
        return False  # Prevent email sending

    config = configparser.ConfigParser()
    config.read('config.ini')

    email_sender = config['email']['sender']
    email_password = config['email']['password']

    if not email_password:
        print("Error: EMAIL_PASSWORD is not set.")
        return

    print(f"Sending email to: {email_recipient} with invoice: {invoice_file_path}")

    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = email_sender
    msg['To'] = email_recipient
    msg['Subject'] = f"Your Invoice_{invoice_file_path.split('_')[-1].split('.')[0]}"  # Extract the invoice number

    # Email body
    body = "Dear Client,\n\nPlease find attached your invoice.\n\nThank you for your business!"
    msg.attach(MIMEText(body, 'plain'))

    # Attach the invoice PDF
    try:
        with open(invoice_file_path, "rb") as attachment:
            part = MIMEApplication(attachment.read(), Name=invoice_file_path)
            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(invoice_file_path)}"'
            msg.attach(part)
    except FileNotFoundError:
        print(f"Error: The file {invoice_file_path} does not exist.")
        return

    # Send the email
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:  # Use SMTP server
            server.starttls()
            server.login(email_sender, email_password)
            server.send_message(msg)
            print("Email sent successfully!")
            return True  # Return True if the email is sent successfully

    except smtplib.SMTPAuthenticationError:
        print("Error: Failed to authenticate with the email server. Check your email and password.")
    except smtplib.SMTPException as e:
        print(f"SMTP Error: {e}")
    except Exception as e:
        print(f"Failed to send email: {e}")

    return False  # Return False if there's an error in sending email