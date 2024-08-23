import requests
import csv

BOLD = '\033[1m'
RESET = '\033[0m'


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


if __name__ == '__main__':
    recommendations_db = get_data()
    statistics = get_average_rating(recommendations_db)
    recommendations_db = find_averages(recommendations_db)
    find_recommendations(recommendations_db)
    find_biggest_deviation(recommendations_db)
    print_stats(statistics)
