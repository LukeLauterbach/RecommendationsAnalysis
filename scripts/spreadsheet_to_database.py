from app import app, db
from models import Item
import json

PARTIPCIANTS = ['Alex', 'Greg', 'Luke', 'Zach']

with open('recommendations.json', 'r') as file:
    recs = json.load(file)

with app.app_context():
    for rec in recs:
        for participant in PARTIPCIANTS:
            try:
                float(rec['Ratings'][participant])
            except ValueError:
                rec['Ratings'][participant] = None

        print(rec)
        new_item = Item(
            name=rec['Title'],
            genre=rec['Genre'],
            where_to_watch=rec['Where to Watch'],
            rating_alex=rec['Ratings']['Alex'],
            rating_greg=rec['Ratings']['Greg'],
            rating_luke=rec['Ratings']['Luke'],
            rating_zach=rec['Ratings']['Zach'],
            rating_average=rec['Average Rating'],
            rating_imdb=rec['IMDb Rating'],
            number_of_ratings=rec['Number of Ratings']
        )
        db.session.add(new_item)

    db.session.commit()
    print("Items added successfully!")
