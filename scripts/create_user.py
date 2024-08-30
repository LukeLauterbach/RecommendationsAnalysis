from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
from models import User

with app.app_context():
    # Hash the password using the correct method
    hashed_password = generate_password_hash('Wolverine1', method='pbkdf2:sha256')

    # Store the hashed password in the database
    new_user = User(username='Luke', password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    print("User created successfully!")