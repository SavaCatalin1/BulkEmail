from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

import smtplib
from email.message import EmailMessage
import os
import time
import threading

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///emails.db'
app.config['SECRET_KEY'] = 'supersecretkey'
db = SQLAlchemy(app)

app.config['SERVER_NAME'] = 'bulkemail-40pb.onrender.com'  # Replace with your domain if running in production
app.config['PREFERRED_URL_SCHEME'] = 'http'   # Use 'https' if your app is served over HTTPS
app.config['APPLICATION_ROOT'] = '/'

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to login page if not logged in

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='user')  # Default role is 'user'

# Load user for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

email_sending_progress = {
    "sent": 0,
    "total": 0,
    "done": False,
    "errors": 0
}

# Database model for storing email addresses
class Email(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    unsubscribed = db.Column(db.Boolean, default=False)

# # Initialize the database
# with app.app_context():
#     db.create_all()
#     print("Database initialized!")


# Home route - form to add new emails and send email campaigns
@app.route('/')
@login_required
def index():
    emails = Email.query.filter_by(unsubscribed=False).all()
    return render_template('index.html', emails=emails)

# Route to add a new email to the database
@app.route('/add_email', methods=['POST'])
@login_required
def add_email():
    email_address = request.form['email']
    if email_address:
        new_email = Email(email=email_address)
        try:
            db.session.add(new_email)
            db.session.commit()
            flash('Email added successfully!', 'success')
        except:
            flash('Email already exists!', 'error')
    return redirect(url_for('index'))

# Route to send emails to all subscribers
@app.route('/send_emails', methods=['POST'])
@login_required
def send_emails():
    global email_sending_progress
    email_sending_progress = {
        "sent": 0,
        "total": 0,
        "done": False,
        "errors": 0
    }

    sender_email = "vanzari@atienergy.ro"
    sender_password = "0#P)Q1RrE=cK"
    subject = "Propunere de instalare a unui sistem de stocare a energiei electrice cu o capacitate utilizabilă de stocare a energiei electrice de cel puțin 5 kW prin PNRR, componenta REPowerEU"
    body = """
Bună ziua,

 

Dacă sunteți interesați să suplimentați instalația fotovoltaică existentă cu un sistem de stocare a energiei electrice cu o capacitate utilizabilă de stocare a energiei electrice de cel puțin 5 kW, prin societatea noastră, vă rugăm să ne trimiteți în replay documentele: copie a cărții de identitate, certificatul de racordare emis/actualizat, extras de carte funciară și, dacă este cazul, contract de ipotecă imobiliară și ultima dovadă a obligațiilor de plată. În cel mai scurt timp vă vom pune la dispoziție o ofertă tehnico-economică pe care, eventual, o vom discuta împreună în prealabil.

 

Vă rugăm să găsiți în atașament un extras din Ghidul Specific PNRR aferent Investiției I4 Schema de granturi sub formă de bonuri valorice pentru accelerarea utilizării energiei din surse regenerabile de către gospodării.

 

 

Departamentul Prosumatori SCM ATI ELECTRIC SRL

Telefon: 0771591747
<img src="https://atienergy.ro/wp-content/uploads/2024/08/ATI-LOGO.png" alt="ATI ENERGY Logo" style="width: 150px; display: block;">

"""
    attachments = [
        'Informare.docx',
        '1.-Ghidul-solicitantului_Investitia-4_.pdf',
        'Ordin_modificare_ghid.pdf'
    ]
    
    # Fetch all subscribed emails
    emails = Email.query.filter_by(unsubscribed=False).all()
    email_sending_progress["total"] = len(emails)
    def send_emails_thread():
        try:
            send_emails_from_list(emails, subject, body, sender_email, sender_password, attachments)
        finally:
            email_sending_progress["done"] = True
    
    threading.Thread(target=send_emails_thread).start()
    return redirect(url_for('email_sending_status'))


# Helper function to send emails
def send_emails_from_list(email_list, subject, body, sender_email, sender_password, attachments, timeout=15):
    with smtplib.SMTP_SSL('mail.atienergy.ro', 465) as smtp:
        smtp.login(sender_email, sender_password)

        # Access the Flask app context here
        with app.app_context():
            for email_entry in email_list:
                try:
                    email = email_entry.email

                    # Create a personalized unsubscribe link
                    unsubscribe_url = url_for('unsubscribe_email', email=email_entry.email, _external=True)

                    # Modify the body to include the unsubscribe button
                    personalized_body = body + f'''
                    <p style="text-align: center; margin-top: 20px;">
                        <a href="{unsubscribe_url}" style="background-color: #e74c3c; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                            Unsubscribe
                        </a>
                    </p>
                    '''

                    msg = EmailMessage()
                    msg['Subject'] = subject
                    msg['From'] = sender_email
                    msg['To'] = email
                    msg.add_alternative(personalized_body, subtype='html')

                    # Add attachments
                    for file_path in attachments:
                        with open(file_path, 'rb') as f:
                            file_data = f.read()
                            file_name = os.path.basename(file_path)
                            msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)

                    smtp.send_message(msg)
                    email_sending_progress["sent"] += 1
                    print(f"Sent email to {email}")
                except Exception as e:
                    email_sending_progress["errors"] += 1
                    print(f"Failed to send email to {email}: {e}")
                time.sleep(timeout)  # Wait before sending the next email

@app.route('/email_sending_status')
@login_required
def email_sending_status():
    return render_template('email_sending_status.html', progress=email_sending_progress)

# Unsubscribe route
@app.route('/unsubscribe/<int:id>')
def unsubscribe(id):
    email = Email.query.get_or_404(id)
    email.unsubscribed = True
    db.session.commit()
    flash(f"{email.email} has been unsubscribed.", 'info')
    return redirect(url_for('index'))

# Route to handle the unsubscribe via email link
@app.route('/unsubscribe_email', methods=['GET'])
def unsubscribe_email():
    email_address = request.args.get('email')
    if email_address:
        email = Email.query.filter_by(email=email_address).first()
        if email:
            email.unsubscribed = True
            db.session.commit()
            return render_template('unsubscribe_confirmation.html', email=email.email)
        else:
            return render_template('unsubscribe_error.html', message="Email not found.")
    return render_template('unsubscribe_error.html', message="No email provided.")

@app.route('/bulk_add_emails', methods=['POST'])
@login_required
def bulk_add_emails():
    # Path to your text file containing emails
    file_path = 'emails.txt'

    # Check if the file exists
    if not os.path.exists(file_path):
        flash("Email file not found.", 'error')
        return redirect(url_for('index'))

    # Open the file and read emails
    with open(file_path, 'r') as f:
        emails = [line.strip() for line in f if line.strip()]

    added_count = 0
    already_exists_count = 0

    # Add emails to the database
    for email_address in emails:
        # Check if email already exists in the database
        existing_email = Email.query.filter_by(email=email_address).first()
        if not existing_email:
            new_email = Email(email=email_address)
            db.session.add(new_email)
            added_count += 1
        else:
            already_exists_count += 1

    try:
        db.session.commit()
        flash(f"{added_count} emails added successfully, {already_exists_count} already existed.", 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while adding emails: {str(e)}", 'error')

    return redirect(url_for('index'))

# Route for user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials. Please try again.', 'error')
    
    return render_template('login.html')

# Route for logging out the user
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# @app.route('/add_user', methods=['GET', 'POST'])
# def add_user():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         role = request.form.get('role', 'user')  # Default role is 'user'

#         # Check if the username already exists
#         existing_user = User.query.filter_by(username=username).first()
#         if existing_user:
#             flash('User already exists!', 'error')
#             return redirect(url_for('add_user'))

#         # Hash the password before storing it in the database
#         hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
#         new_user = User(username=username, password=hashed_password, role=role)
#         db.session.add(new_user)
#         db.session.commit()
        
#         flash('User added successfully!', 'success')
#         return redirect(url_for('index'))
    
#     return render_template('add_user.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
