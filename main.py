import re
from PyPDF2 import PdfReader
from email_validator import validate_email, EmailNotValidError

# Function to extract emails from PDF table
def extract_emails_from_pdf(pdf_path, output_file):
    reader = PdfReader(pdf_path)
    emails = set()
    email_column_header = "Adresa e-mail"

    for page in reader.pages:
        text = page.extract_text()

        # Split the text into lines
        lines = text.splitlines()
        
        # Identify the header line
        header_line_index = -1
        for i, line in enumerate(lines):
            if email_column_header in line:
                header_line_index = i
                break
        
        # If header line found, extract emails from the corresponding column
        if header_line_index != -1:
            for line in lines[header_line_index + 1:]:
                # Attempt to extract email using regex from each line
                email_match = re.search(r'[\w\.-]+@[\w\.-]+', line)
                if email_match:
                    email = email_match.group(0)
                    try:
                        # Validate the email
                        valid = validate_email(email).email
                        emails.add(valid)
                    except EmailNotValidError:
                        continue

    # Write the valid emails to the output file
    with open(output_file, 'w') as f:
        for email in emails:
            f.write(email + '\n')

    print(f"Extracted {len(emails)} emails and saved to {output_file}")

# Path to your PDF file and output file
pdf_path = './data.pdf'
output_file = 'extracted_emails.txt'

# Extract emails and save to a file
extract_emails_from_pdf(pdf_path, output_file)
