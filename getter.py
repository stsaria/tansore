import csv

def get_personal_data(csv_file : str):
    data = {}
    with open(csv_file, encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            data[row[0]] = [row[1], row[2]]
    return data