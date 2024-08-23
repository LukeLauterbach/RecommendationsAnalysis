import requests
import csv


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
            'Alex': row[4],
            'Luke': row[5],
            'Zach': row[6],
            'Greg': row[7],
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
        for key, value in rec.items():
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
        print(f"{stat_dictionary_name}")
        for key, value in stat_dictionary_items.items():
            print(f"{key}: {value}")
        print()


if __name__ == '__main__':
    recommendations_db = get_data()
    statistics = get_average_rating(recommendations_db)
    print_stats(statistics)