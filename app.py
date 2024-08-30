from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from models import db, User, Item
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

PARTICIPANTS = ['alex', 'greg', 'luke', 'zach']

with app.app_context():
    db.create_all()


# ----------------------------------------- #
# FUNCTIONS                                 #
# ----------------------------------------- #

def authenticate_and_redirect(route):
    if 'user_id' not in session:
        return redirect(url_for(route))
    return None


def calculate_average_rating(item):
    ratings = [item.rating_alex, item.rating_greg, item.rating_luke, item.rating_zach]
    ratings = [item for item in ratings if item is not None]  # Remove all null values
    converted_ratings = []
    for item in ratings:
        try:
            converted_ratings.append(float(item))
        except ValueError:  # Optionally handle cases where conversion fails, but assuming no null values
            continue
    ratings = converted_ratings
    average = sum(rating for rating in ratings if rating is not None) / len(ratings)
    return average


# ----------------------------------------- #
# ROUTES                                    #
# ----------------------------------------- #

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        else:
            return 'Invalid credentials'
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    redirect_response = authenticate_and_redirect('login')
    if redirect_response:
        return redirect_response

    items = Item.query.all()
    return render_template('dashboard.html', items=items)


@app.route('/add_new_entry', methods=['POST'])
def add_new_entry():
    data = request.get_json()

    # Provide default values for missing fields
    title = data.get('title', '')
    type_ = data.get('type', 'TV')
    description = data.get('description', '')

    new_item = Item(
        name=title,
        genre=type_,
        description=description,
    )
    for participant in PARTICIPANTS:
        if data[f"rating_{participant}"]:
            setattr(new_item, f"rating_{participant}", float(data[f"rating_{participant}"]))
        else:
            setattr(new_item, f"rating_{participant}", None)

    new_item.average = calculate_average_rating(new_item)
    import utils.imdb as imdb
    new_item = imdb.imdb_lookup(new_item)

    try:
        db.session.add(new_item)
        db.session.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/delete_item/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    redirect_response = authenticate_and_redirect('login')
    if redirect_response:
        return redirect_response

    item = Item.query.get(item_id)
    if item:
        db.session.delete(item)
        db.session.commit()
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error', 'message': 'Item not found'}), 404


@app.route('/update_rating', methods=['POST'])
def update_rating():
    data = request.get_json()
    item_id = data.get('item_id')
    rating_type = data.get('rating_type')
    rating_value = data.get('rating_value', None)  # Convert rating_value to float
    if rating_value:
        rating_value = float(rating_value)
    else:
        rating_value = None

    # Validate input
    if not item_id or not rating_type:
        return jsonify({'status': 'error', 'message': 'Invalid input'}), 400

    # Update the rating in the database
    item = Item.query.get(item_id)
    if not item:
        return jsonify({'status': 'error', 'message': 'Item not found'}), 404

    # Update the rating based on the rating_type
    if rating_type == 'alex':
        item.rating_alex = rating_value
    elif rating_type == 'greg':
        item.rating_greg = rating_value
    elif rating_type == 'luke':
        item.rating_luke = rating_value
    elif rating_type == 'zach':
        item.rating_zach = rating_value
    else:
        return jsonify({'status': 'error', 'message': 'Invalid rating type'}), 400

    item.rating_average = calculate_average_rating(item)  # Recalculate average rating

    # Commit changes to the database
    db.session.commit()

    return jsonify({'status': 'success', 'average_rating': item.rating_average})


@app.route('/get_item_details/<int:item_id>')
def get_item_details(item_id):
    item = Item.query.get(item_id)
    if item:
        return jsonify({
            'status': 'success',
            'name': item.name,
            'rating_alex': item.rating_alex,
            'rating_greg': item.rating_greg,
            'rating_luke': item.rating_luke,
            'rating_zach': item.rating_zach,
            'rating_imdb': item.rating_imdb,
            'description': item.description,
            'imdb_id': item.imdb_id,
            'poster': item.poster,
            'year': item.year,
            'box_office': item.box_office
        })
    return jsonify({'status': 'error', 'message': 'Item not found'}), 404


@app.route('/get_items', methods=['GET'])
def get_items():
    redirect_response = authenticate_and_redirect('login')
    if redirect_response:
        return redirect_response

    try:
        items = Item.query.all()
        items_list = [
            {
                'id': item.id,
                'title': item.name,
                'type': item.genre,
                'description': item.description,
                'rating_alex': item.rating_alex,
                'rating_luke': item.rating_luke,
                'rating_greg': item.rating_greg,
                'rating_zach': item.rating_zach,
                'rating_average': item.rating_average,
                'rating_imdb': item.rating_imdb,
                'number_of_ratings': item.number_of_ratings,
                'imdb_id': item.imdb_id,
                'genre': item.genre,
                'poster': item.poster,
                'box_office': item.box_office
            }
            for item in items
        ]
        return jsonify({'items': items_list})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/update_description', methods=['POST'])
def update_description():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Not authorized'}), 401

    data = request.get_json()
    item_id = data.get('item_id')
    new_description = data.get('description')

    item = Item.query.get(item_id)
    if item:
        item.description = new_description
        db.session.commit()
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error', 'message': 'Item not found'}), 404


@app.route('/update_imdb_id', methods=['POST'])
def update_imdb_id():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Not authorized'}), 401

    data = request.get_json()
    item_id = data.get('item_id')
    new_imdb_id = data.get('imdb_id')

    item = Item.query.get(item_id)
    import utils.imdb as imdb
    item = imdb.imdb_lookup_id(item)
    if item:
        item.imdb_id = new_imdb_id
        db.session.commit()
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error', 'message': 'Item not found'}), 404


@app.route('/statistics')
def statistics():
    redirect_response = authenticate_and_redirect('login')
    if redirect_response:
        return redirect_response

    # Query to find the item with the highest average of Alex, Greg, and Zach ratings but without Luke's rating
    highest_rated_item = db.session.query(Item).filter(Item.rating_luke.is_(None)).order_by(
        (Item.rating_alex + Item.rating_greg + Item.rating_zach) / 3).first()

    imdb_diffs = []
    users = ['Alex', 'Greg', 'Luke', 'Zach']
    for user in users:
        user = user.lower()
        difference = db.session.query(
            Item,
            (getattr(Item, f"rating_{user}") - Item.rating_imdb).label('difference')
        ).filter(getattr(Item, f"rating_{user}") .isnot(None), Item.rating_imdb.isnot(None)).order_by(
            db.func.abs(getattr(Item, f"rating_{user}")  - Item.rating_imdb).desc()
        ).first()
        imdb_diffs.append({'Person': user.capitalize(),
                           'Title': difference.Item.name,
                           'Rating': difference.Item.rating_luke,
                           'IMDBRating': difference.Item.rating_imdb,
                           'Difference': difference.difference})

    # Sort the list
    imdb_diffs = sorted(imdb_diffs, key=lambda x: abs(x['Difference']), reverse=True)

    return render_template('statistics.html', imdb_diffs=imdb_diffs)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
