from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
from models import User

USERS = ['alex', 'greg', 'luke', 'zach']

with app.app_context():
    # Hash the password using the correct method
    hashed_password = generate_password_hash('SAU123', method='pbkdf2:sha256')

    for user in USERS:
        new_user = User(username=user, password=hashed_password)
        db.session.add(new_user)
    db.session.commit()
    print("User(s) created successfully!")