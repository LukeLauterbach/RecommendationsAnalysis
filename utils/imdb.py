import json
import requests
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

OMDB_KEY = os.getenv('OMDB_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


def imdb_lookup(item):
    item_name = item.name
    # Load the local cache of the OMDB data
    try:
        with open('ContentDBData.json', 'r') as json_file:
            content_db = json.load(json_file)
    except FileNotFoundError:
        content_db = {}

    if item_name not in content_db:
        print(f"Looking Up: {item_name}")
        content_db[item_name] = get_internet_rating(rec_name=item_name)
        if not content_db[item_name]:
            print(f"Error Looking Up {item_name}")
            return item
        else:
            with open('ContentDBData.json', 'w') as json_file:
                json.dump(content_db, json_file)

    content_db_entry = content_db[item_name]

    try:
        item.box_office = content_db_entry['BoxOffice']
        item.box_office = item.box_office.replace('$', '').replace(',', '')
    except KeyError:
        item.box_office = 0
    except ValueError:
        item.box_office = 0

    item.poster = content_db_entry['Poster']
    item.rating = content_db_entry['imdbRating']
    item.imdb_id = content_db_entry['imdbID']
    item.genre = content_db_entry['Genre']
    item.rating_imdb = content_db_entry['imdbRating']
    item.year = content_db_entry['Year']

    try:
        item.box_office = content_db_entry['BoxOffice']
        item.box_office = item.box_office.replace('$', '').replace(',', '')
    except KeyError:
        item.box_office = 0
    except ValueError:
        item.box_office = 0

    return item


def imdb_lookup_id(item):
    item_id = item.imdb_id
    # Load the local cache of the OMDB data
    try:
        with open('ContentDBData.json', 'r') as json_file:
            content_db = json.load(json_file)
    except FileNotFoundError:
        content_db = {}

    if item_id not in content_db:
        print(f"Looking Up: {item_id}")
        content_db[item_id] = get_internet_rating(imdb_id=item_id)
        print(content_db[item_id])
        if not content_db[item_id]:
            print(f"Error Looking Up {item_id}")
            return
        else:
            with open('ContentDBData.json', 'w') as json_file:
                json.dump(content_db, json_file)

    content_db_entry = content_db[item_id]
    item.poster = content_db_entry['Poster']
    item.rating = content_db_entry['imdbRating']
    item.imdb_id = content_db_entry['imdbID']
    item.genre = content_db_entry['Genre']
    item.rating_imdb = content_db_entry['imdbRating']
    item.year = content_db_entry['Year']
    item.name = content_db_entry['Title']
    print(item.rating)

    try:
        item.box_office = content_db_entry['BoxOffice']
        if item.box_office == "N/A":
            item.box_office = 0
        else:
            item.box_office = item.box_office.replace('$', '').replace(',', '')
    except KeyError:
        item.box_office = 0
    except ValueError:
        item.box_office = 0

    print(item)
    return item


def get_proper_name(name_to_fix):
    client = OpenAI(api_key=OPENAI_API_KEY)
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"What is the name of this show or movie on IMDb? Provide only the name, not anything else. "
                           f"{name_to_fix}",
            }
        ],
        model="gpt-4o-mini",
    )
    fixed_name = chat_completion.choices[0].message.content
    print(f"OpenAI Fixed Name: '{name_to_fix}' to '{fixed_name}'")
    return fixed_name


def fix_name(name_to_fix):
    try:
        with open('NameFixes.json', 'r') as json_file:
            name_fixes_db = json.load(json_file)
    except FileNotFoundError:
        name_fixes_db = {}

    try:
        fixed_name = name_fixes_db[name_to_fix]
        return fixed_name
    except KeyError:
        fixed_name = get_proper_name(name_to_fix)
        name_fixes_db[name_to_fix] = fixed_name

    with open('NameFixes.json', 'w') as json_file:
        json.dump(name_fixes_db, json_file)


def get_internet_rating(rec_name="", imdb_id=""):
    url = "http://www.omdbapi.com/"
    params = {'apikey': OMDB_KEY}
    if rec_name:
        params['t'] = rec_name
    elif imdb_id:
        params['i'] = imdb_id
    else:
        print("Erorr: No Search Criterea Provided (get_internet_rating)")

    # Make the request to the OMDb API
    response = requests.get(url, params=params)

    # Check if the request was successful
    if response.status_code == 200 and 'Error' not in str(response.json()):
        movie_data = response.json()
        return movie_data

    # Handle mistyped names
    rec_name = fix_name(rec_name)
    params['t'] = rec_name
    response = requests.get(url, params=params)
    if response.status_code == 200 and 'Error' not in str(response.json()):
        movie_data = response.json()
        return movie_data
    else:
        print(f"Error: {response.status_code} ({rec_name})")
