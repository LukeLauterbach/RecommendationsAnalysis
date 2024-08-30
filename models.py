from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    box_office = db.Column(db.Float, nullable=True)
    imdb_id = db.Column(db.String(40), nullable=True)
    name = db.Column(db.String(80), nullable=False)
    poster = db.Column(db.String(120), nullable=True)
    year = db.Column(db.Integer(), nullable=True)
    format = db.Column(db.String(20), nullable=True)
    genre = db.Column(db.String(80), nullable=True)
    where_to_watch = db.Column(db.String(80), nullable=True)
    rating_alex = db.Column(db.Float, nullable=True)
    rating_greg = db.Column(db.Float, nullable=True)
    rating_luke = db.Column(db.Float, nullable=True)
    rating_zach = db.Column(db.Float, nullable=True)
    rating_average = db.Column(db.Float, nullable=True)
    rating_imdb = db.Column(db.Float, nullable=True)
    number_of_ratings = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text, nullable=True)
