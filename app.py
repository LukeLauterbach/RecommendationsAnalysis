from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from models import db, User, Item
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()


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
    if 'user_id' not in session:
        return redirect(url_for('login'))

    items = Item.query.all()
    return render_template('dashboard.html', items=items)


@app.route('/add_new_entry', methods=['POST'])
def add_new_entry():
    data = request.get_json()

    # Provide default values for missing fields
    title = data.get('title', '')
    type_ = data.get('type', 'TV')
    description = data.get('description', '')
    rating_alex = float(data.get('rating_alex', 0))
    rating_luke = float(data.get('rating_luke', 0))
    rating_greg = float(data.get('rating_greg', 0))
    rating_zach = float(data.get('rating_zach', 0))

    # Calculate average rating (example calculation)
    average_rating = (rating_alex + rating_luke + rating_greg + rating_zach) / 4

    new_item = Item(
        name=title,
        genre=type_,
        description=description,
        rating_alex=rating_alex,
        rating_luke=rating_luke,
        rating_greg=rating_greg,
        rating_zach=rating_zach,
        rating_average=average_rating
    )

    try:
        db.session.add(new_item)
        db.session.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/delete_item/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Not authorized'}), 401

    item = Item.query.get(item_id)
    if item:
        db.session.delete(item)
        db.session.commit()
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error', 'message': 'Item not found'}), 404


@app.route('/update_rating', methods=['POST'])
def update_rating():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Not authorized'}), 401

    item_id = request.json.get('item_id')
    rating_type = request.json.get('rating_type')
    new_rating = request.json.get('new_rating')

    item = Item.query.get(item_id)
    if item:
        if rating_type == 'alex':
            item.rating_alex = new_rating if new_rating else None
        elif rating_type == 'greg':
            item.rating_greg = new_rating if new_rating else None
        elif rating_type == 'luke':
            item.rating_luke = new_rating if new_rating else None
        elif rating_type == 'zach':
            item.rating_zach = new_rating if new_rating else None
        db.session.commit()
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error', 'message': 'Item not found'}), 404


@app.route('/get_item_details/<int:item_id>')
def get_item_details(item_id):
    item = Item.query.get(item_id)
    if item:
        return jsonify({
            'name': item.name,
            'rating_alex': item.rating_alex,
            'rating_greg': item.rating_greg,
            'rating_luke': item.rating_luke,
            'rating_zach': item.rating_zach,
            'rating_imdb': item.rating_imdb,
            'description': item.description
        })
    return jsonify({'status': 'error', 'message': 'Item not found'}), 404


@app.route('/get_items', methods=['GET'])
def get_items():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Not authorized'}), 401

    try:
        items = Item.query.all()
        items_list = [
            {
                'title': item.name,
                'type': item.genre,
                'description': item.description,
                'rating_alex': item.rating_alex,
                'rating_luke': item.rating_luke,
                'rating_greg': item.rating_greg,
                'rating_zach': item.rating_zach,
                'rating_average': item.rating_average,
                'rating_imdb': item.rating_imdb,
                'number_of_ratings': item.number_of_ratings
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


@app.route('/statistics')
def statistics():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Query to find the item with the highest average of Alex, Greg, and Zach ratings but without Luke's rating
    highest_rated_item = db.session.query(Item).filter(Item.rating_luke.is_(None)).order_by(
        (Item.rating_alex + Item.rating_greg + Item.rating_zach) / 3).first()

    items_with_difference = db.session.query(
        Item,
        (Item.rating_luke - Item.rating_imdb).label('difference')
    ).filter(Item.rating_luke.isnot(None), Item.rating_imdb.isnot(None)).order_by(
        db.func.abs(Item.rating_luke - Item.rating_imdb).desc()
    ).first()

    return render_template('statistics.html', item=items_with_difference)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
