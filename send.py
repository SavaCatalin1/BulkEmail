import smtplib
import time
from email.message import EmailMessage
import os

# Function to send emails with attachments and timeout
def send_emails_from_file(email_file, subject, body, sender_email, sender_password, attachments, timeout=60):
    # Read emails from the file
    with open(email_file, 'r') as f:
        email_list = [line.strip() for line in f if line.strip()]

    # Using smtplib to send the email
    with smtplib.SMTP_SSL('mail.atienergy.ro', 465) as smtp:
        smtp.login(sender_email, sender_password)
        for email in email_list:
            msg = EmailMessage()
            msg['Subject'] = subject
            msg['From'] = sender_email
            msg['To'] = email
            msg.add_alternative(body, subtype='html')

            # Add attachments
            for file_path in attachments:
                try:
                    with open(file_path, 'rb') as f:
                        file_data = f.read()
                        file_name = os.path.basename(file_path)
                        msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)
                except Exception as e:
                    print(f"Failed to attach file {file_path}: {e}")

            # Send the email
            smtp.send_message(msg)
            print(f"Sent email to {email}")
            time.sleep(timeout)  # Wait before sending the next email

# Email details
email_file = 'extracted_emails.txt'
subject = "Super preturi la invertoare! - ATI ENERGY"
body = """
<table role="presentation" style="font-family: Arial, sans-serif; color: #333333; width: 100%; max-width: 100%; margin: auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 10px;" cellspacing="0" cellpadding="0">
    
    <!-- Logo Section -->
    <tr>
        <td align="center" style="padding-bottom: 20px;">
            <img src="https://atienergy.ro/wp-content/uploads/2024/08/ATI-LOGO.png" alt="ATI ENERGY Logo" style="width: 150px; display: block;">
        </td>
    </tr>

    <!-- Main Message Section -->
    <tr>
        <td style="background-color: #f8f8f8; padding: 20px; border-radius: 10px;">
            <h1 style="font-size: 24px; color: #2c3e50; text-align: center; margin: 0;">Avem vești bune!</h1>
            <p style="font-size: 18px; line-height: 1.6; text-align: center; margin: 16px 0;">
                La <strong style="color: #e74c3c;">ATI ENERGY</strong> suntem pe punctul de a lichida stocul de invertoare și vrem să vă oferim prima șansă la aceste super oferte.
            </p>
            <p style="font-size: 20px; font-weight: bold; color: #27ae60; text-align: center; margin: 16px 0;">
                Grăbiți-vă, stocul este limitat!
            </p>
        </td>
    </tr>
    
    <!-- Contact Information Section -->
    <tr>
        <td style="padding-top: 30px; text-align: center;">
            <p style="font-size: 16px; color: #7f8c8d; margin: 0;">
                Echipa ATI ENERGY<br>
                <a href="tel:+40770292001" style="color: #2980b9; text-decoration: none;">+40 770 292 001</a>
            </p>
        </td>
    </tr>

    <!-- Call to Action Button -->
    <tr>
        <td style="text-align: center; padding-top: 20px;">
            <a href="https://atienergy.ro/contact" style="font-size: 18px; color: white; background-color: #e74c3c; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                Contactează-ne acum
            </a>
        </td>
    </tr>

     <!-- Unsubscribe Section -->
    <tr>
        <td style="text-align: center; padding-top: 20px;">
            <p style="font-size: 12px; color: #bdc3c7; margin: 0;">
                Dacă nu mai doriți să primiți emailuri de la noi, 
                <a href="mailto:unsubscribe@yourdomain.com?subject=Unsubscribe&body=Please remove my email: {{email}}" style="color: #2980b9;">faceți clic aici</a> pentru a vă dezabona.
            </p>
        </td>
    </tr>

    <!-- Image Row -->
    <tr>
        <td style="padding-top: 40px;">
            <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
                <tr>
                    <td style="padding: 5px; width: 33.33%;" align="center">
                        <img src="https://atienergy.ro/wp-content/uploads/2024/08/Oferta-Invertor-Huawei-SUN2000-3KTL-L1.jpg" alt="Huawei SUN2000 3KTL-L1" style="width: 100%; max-width: 90%; border-radius: 10px; display: block;">
                    </td>
                    <td style="padding: 5px; width: 33.33%;" align="center">
                        <img src="https://atienergy.ro/wp-content/uploads/2024/08/Oferta-Invertor-Huawei-SUN2000-4KTL-L1.jpg" alt="Huawei SUN2000 4KTL-L1" style="width: 100%; max-width: 90%; border-radius: 10px; display: block;">
                    </td>
                    <td style="padding: 5px; width: 33.33%;" align="center">
                        <img src="https://atienergy.ro/wp-content/uploads/2024/08/Oferta-Invertor-Huawei-SUN2000-5KTL-L1.jpg" alt="Huawei SUN2000 5KTL-L1" style="width: 100%; max-width: 90%; border-radius: 10px; display: block;">
                    </td>
                </tr>
            </table>
        </td>
    </tr>

    <!-- Footer Section -->
    <tr>
        <td style="text-align: center; padding-top: 40px;">
            <p style="font-size: 12px; color: #bdc3c7; margin: 0;">&copy; 2024 ATI ENERGY. Toate drepturile rezervate.</p>
        </td>
    </tr>

</table>
"""


sender_email = "vanzari@atienergy.ro"
sender_password = "0#P)Q1RrE=cK"

# List of file paths to attach
attachments = [
    'Oferta Invertor Huawei SUN2000 3KTL-L1.png',
    'Oferta Invertor Huawei SUN2000 4KTL-L1.png',
    'Oferta Invertor Huawei SUN2000 5KTL-L1.png'
]

# Send emails with a 15-second timeout between each to avoid being blocked
send_emails_from_file(email_file, subject, body, sender_email, sender_password, attachments, timeout=15)
