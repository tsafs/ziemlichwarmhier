import csv
import re

input_path = './data/KL_Tageswerte_Beschreibung_Stationen.txt'
output_path = 'station_date_ranges.csv'

with open(input_path, encoding='latin1') as f:
    lines = f.readlines()

# Skip header lines (first 2)
data_lines = lines[2:]

rows = []
for line in data_lines:
    # Use regex to split by whitespace, but keep station names with spaces together
    parts = re.split(r'\s+', line.strip(), maxsplit=7)
    if len(parts) < 7:
        continue
    station_id = parts[0]
    von_datum = parts[1]
    bis_datum = parts[2]
    geoBreite = parts[4]
    geoLaenge = parts[5]
    rows.append([station_id, von_datum, bis_datum, geoBreite, geoLaenge])

with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['station_id', 'von_datum', 'bis_datum', 'geoBreite', 'geoLaenge'])
    writer.writerows(rows)