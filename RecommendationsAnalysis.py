import requests
import csv
import json
from openai import OpenAI
import os

BOLD = '\033[1m'
RESET = '\033[0m'
PARTICIPANTS = ['Luke', 'Zach', 'Greg', 'Alex']
OMDB_KEY = os.getenv('OMDB_KEY')
OPENAI_KEY = os.getenv('OPENAI_KEY')

if not OMDB_KEY:
    raise ValueError("API key not found. Please set the OMDB_API_KEY environment variable.")
if not OPENAI_KEY:
    raise ValueError("API key not found. Please set the OPENAI_KEY environment variable.")


def get_data():
    url = f"https://docs.google.com/spreadsheets/d/1U409HimWlvbda3F2x38w8ZFvOLbC4kA-qxtT_NAFx0I/export?format=csv"
    response = requests.get(url)
    response_text = response.text

    # Parse the CSV content
    csv_reader = csv.reader(response_text.splitlines())
    rec_db = []
    for row in csv_reader:
        rec_db.append({
            'Title': row[0],
            'Format': row[1],
            'Genre': row[2],
            'Where to Watch': row[3],
            'Ratings': {
                'Alex': row[4],
                'Luke': row[5],
                'Zach': row[6],
                'Greg': row[7]
            },
            'Luke Notes': row[8],
            'Alex Notes': row[9],
            'Zach Notes': row[10],
            'Greg Notes': row[11],
            'IMDb Rating': None
        })

    return rec_db[1:]


def get_average_rating(rec_db):
    stats = {
        'Totals': {
            'Luke': 0,
            'Zach': 0,
            'Greg': 0,
            'Alex': 0
        },
        'Averages': {
            'Luke': 0,
            'Zach': 0,
            'Greg': 0,
            'Alex': 0
        },
        'Counts': {
            'Luke': 0,
            'Zach': 0,
            'Greg': 0,
            'Alex': 0
        },
        'To Watch': {
            'Luke': 0,
            'Zach': 0,
            'Greg': 0,
            'Alex': 0
        }
    }

    for rec in rec_db:
        for key, value in rec['Ratings'].items():
            for stat_name, stat_value in stats['Totals'].items():
                if key == stat_name:
                    try:
                        stats['Totals'][stat_name] += float(value)
                        stats['Counts'][stat_name] += 1
                    except ValueError:
                        if value.lower() == "w":
                            stats['To Watch'][stat_name] += 1

    for key, value in stats['Averages'].items():
        stats['Averages'][key] = stats['Totals'][key] / stats['Counts'][key]

    del stats['Totals']

    # Sort Metrics
    stats['Averages'] = dict(sorted(stats['Averages'].items(), key=lambda x: x[1], reverse=True))
    stats['Counts'] = dict(sorted(stats['Counts'].items(), key=lambda x: x[1], reverse=True))
    stats['To Watch'] = dict(sorted(stats['To Watch'].items(), key=lambda x: x[1], reverse=True))

    return stats


def print_stats(stats):
    for stat_dictionary_name, stat_dictionary_items in stats.items():
        print(f"{BOLD}{stat_dictionary_name}{RESET}")
        for key, value in stat_dictionary_items.items():
            print(f"{key}: {value}")
        print()


def find_averages(rec_db):
    for i in range(0, len(rec_db)):
        total_rating = 0.0
        num_ratings = 0
        for reviewer, rating in rec_db[i]['Ratings'].items():
            try:
                total_rating += float(rating)
                num_ratings += 1
            except ValueError:
                pass

        if num_ratings != 0:
            average_rating = total_rating / num_ratings
        else:
            average_rating = 0

        rec_db[i]['Average Rating'] = average_rating
        rec_db[i]['Number of Ratings'] = num_ratings

    return rec_db


def find_recommendations(rec_db):
    recommendations = [
        {'Person': 'Luke', 'Recommendation': '', 'Rating': 0},
        {'Person': 'Zach', 'Recommendation': '', 'Rating': 0},
        {'Person': 'Greg', 'Recommendation': '', 'Rating': 0},
        {'Person': 'Alex', 'Recommendation': '', 'Rating': 0}
    ]

    for rec in rec_db:
        if rec['Number of Ratings'] != 3:
            continue
        for i in range(0, len(recommendations)):
            if rec['Ratings'][recommendations[i]['Person']]:
                continue
            if rec['Average Rating'] > recommendations[i]['Rating']:
                recommendations[i]['Recommendation'] = rec['Title']
                recommendations[i]['Rating'] = rec['Average Rating']

    print(f"{BOLD}Recommended Next Watch{RESET}")
    for recommendation in recommendations:
        if not recommendation['Recommendation']:
            print(f"{recommendation['Person']}: No Recommendations")
            continue
        print(f"{recommendation['Person']}: {recommendation['Recommendation']} (Rating: {recommendation['Rating']})")
    print()


def find_biggest_deviation(rec_db):
    deviation = [
        {'Person': 'Luke', 'Recommendation': '', 'Difference': 0},
        {'Person': 'Zach', 'Recommendation': '', 'Difference': 0},
        {'Person': 'Greg', 'Recommendation': '', 'Difference': 0},
        {'Person': 'Alex', 'Recommendation': '', 'Difference': 0}
    ]

    for rec in rec_db:
        for i in range(0, len(deviation)):
            if not rec['Ratings'][deviation[i]['Person']]:
                continue
            if rec['Number of Ratings'] < 3:
                continue
            try:
                dev = abs(float(rec['Ratings'][deviation[i]['Person']]) - rec['Average Rating'])
            except ValueError:
                continue
            if dev > deviation[i]['Difference']:
                deviation[i]['Difference'] = dev
                deviation[i]['Recommendation'] = rec['Title']

    print(f"{BOLD}Biggest Deviation from The Group{RESET}")
    for dev in deviation:
        print(f"{dev['Person']}: {dev['Recommendation']} (Difference: {dev['Difference']})")
    print()


def get_internet_rating(rec_name, omdb_key="901e6e28"):
    url = "http://www.omdbapi.com/"
    params = {
        't': rec_name,
        'apikey': OMDB_KEY
    }

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


def check_internet_data(rec_db):
    # Load the local cache of the OMDB data
    try:
        with open('ContentDBData.json', 'r') as json_file:
            content_db = json.load(json_file)
    except FileNotFoundError:
        content_db = {}

    for i in range(len(rec_db)):
        rec_name = rec_db[i]['Title']
        if rec_name not in content_db:
            print(f"Looking Up: {rec_name}")
            content_db[rec_name] = get_internet_rating(rec_name)
            if not content_db[rec_name]:
                print(f"Error Looking Up {rec_name}")
                exit()
            with open('ContentDBData.json', 'w') as json_file:
                json.dump(content_db, json_file)

        # Add the IMDb Rating to the rec_db
        if content_db[rec_name]['imdbRating'] == 'N/A':
            rec_db[i]['IMDb Rating'] = None
        else:
            rec_db[i]['IMDb Rating'] = float(content_db[rec_name]['imdbRating'])
        try:
            rec_db[i]['Poster'] = content_db[rec_name]['Poster']
            rec_db[i]['Year'] = content_db[rec_name]['Year']
            rec_db[i]['IMDB ID'] = content_db[rec_name]['imdbID']
        except ValueError:
            print(f"Error Looking Up:")
            print(rec_db[i])
            print(content_db[rec_name])
        try:
            rec_db[i]['Box Office'] = content_db[rec_name]['BoxOffice']
            rec_db[i]['Box Office'] = int(rec_db[i]['Box Office'].replace('$', '').replace(',', ''))
        except KeyError:
            rec_db[i]['Box Office'] = 0
        except ValueError:
            rec_db[i]['Box Office'] = 0

    return rec_db


def get_diff_from_internet(rec_db):
    biggest_diff = {name: {'Recommendation': "", 'Difference': 0} for name in PARTICIPANTS}

    for rec in rec_db:
        for person, diff_rec in biggest_diff.items():
            if not rec['Ratings'][person] or not rec['IMDb Rating']:
                continue
            try:
                float(rec['Ratings'][person])
            except ValueError:
                continue
            diff = float(rec['Ratings'][person]) - rec['IMDb Rating']
            if abs(diff) > abs(diff_rec['Difference']):
                biggest_diff[person]['Recommendation'] = rec['Title']
                biggest_diff[person]['Difference'] = diff


def get_proper_name(name_to_fix):
    client = OpenAI(api_key=OPENAI_KEY)
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


def find_biggest_inet_diff(rec_db):
    statistics = {"Rating Count": {participant: 0 for participant in PARTICIPANTS},
                  "Difference": {participant: 0 for participant in PARTICIPANTS},
                  "Avg Diff": {participant: 0 for participant in PARTICIPANTS},
                  "Biggest Diff": {participant: {"Rec Title": "", "Diff": 0} for participant in PARTICIPANTS}}
    for rec in rec_db:
        for participant in PARTICIPANTS:
            if not rec['Ratings'][participant] or not rec['IMDb Rating']:
                continue
            try:
                rating = float(rec['Ratings'][participant])
            except ValueError:
                continue
            diff = rating - rec['IMDb Rating']
            statistics['Difference'][participant] += diff
            statistics['Rating Count'][participant] += 1
            if abs(diff) > abs(statistics['Biggest Diff'][participant]['Diff']):
                statistics['Biggest Diff'][participant]['Rec Title'] = rec['Title']
                statistics['Biggest Diff'][participant]['Diff'] = diff

    # Calculate Results
    #for participant in PARTICIPANTS:
    #    statistics['Avg Diff'][participant] = (statistics['Difference'][participant] /
    #                                           statistics['Rating Count'][participant])

    # Sort Results
    statistics['Avg Diff'] = dict(sorted(statistics['Avg Diff'].items(), key=lambda item: item[1]))

    # Print Results
    print(f"{BOLD}Average Deviation from IMDb{RESET}")
    for participant, diff in statistics['Avg Diff'].items():
        print(f"{participant}: {round(diff, 2)}")
    print(f"\n{BOLD}Biggest Deviation from IMDb{RESET}")
    for participant, data in statistics['Biggest Diff'].items():
        print(f"{participant}: {data['Rec Title']} ({round(data['Diff'],2)})")


def write_rec_db(rec_db):
    with open('recommendations.json', 'w') as json_file:
        json.dump(rec_db, json_file)


if __name__ == '__main__':
    recommendations_db = get_data()
    #statistics = get_average_rating(recommendations_db)
    recommendations_db = find_averages(recommendations_db)
    recommendations_db = check_internet_data(recommendations_db)
    #find_recommendations(recommendations_db)
    find_biggest_deviation(recommendations_db)
    #print_stats(statistics)
    #find_biggest_inet_diff(recommendations_db)
    write_rec_db(recommendations_db)