from app import app, db
from models import Item

with app.app_context():
    db.drop_all()
    db.create_all()
    print("Dropped and recreated all tables successfully!")
