from application import db, app

# Initialize the database
with app.app_context():
    db.create_all()
    print("Database initialized!")
