from app import app, db, calculate_weighted_rating
from models import Item
import json

PARTIPCIANTS = ['Alex', 'Greg', 'Luke', 'Zach']

with open('../recommendations.json', 'r') as file:
    recs = json.load(file)

with app.app_context():
    for rec in recs:
        for participant in PARTIPCIANTS:
            try:
                float(rec['Ratings'][participant])
            except ValueError:
                rec['Ratings'][participant] = None
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
            number_of_ratings=rec['Number of Ratings'],
            imdb_id=rec['IMDB ID'],
            poster=rec['Poster'],
            box_office=rec['Box Office'],
            year=rec['Year'],
        )
        db.session.add(new_item)

    db.session.commit()
    print("Items added successfully!")

    # Update weighted rankings
    for item in Item.query.all():
        item.weighted_rating = calculate_weighted_rating(item)
    db.session.commit()
    print("Weighted ratings successfully set!")