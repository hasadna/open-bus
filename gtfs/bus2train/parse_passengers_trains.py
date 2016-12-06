"""
Script for adjusting data from Rakevet Israel before uploading to PostGRES
The script does 3 things:
1. add comma on rows with missing n_passengers
2. replace Rakevet Israel name convention to stop_code
3. add column Day
"""

import csv
import argparse
from datetime import datetime
import calendar


def create_dict_of_stations(dict_stations_path):
    with open(dict_stations_path, mode='r', encoding='utf8') as infile:
        reader = csv.reader(infile)
        station_dict = {rows[0]: rows[1] for rows in reader}
        return station_dict


def main(data_path, dict_path,output_path):
    text = ""
    station_dict = create_dict_of_stations(dict_path)
    with open(data_path, 'r', encoding='utf8') as f:
        reader = csv.reader(f)
        for line in reader:
            if len(line) < 4:  # fix missing values
                line.append('')
            if line[0] != "destination_station":
                line[0] = station_dict[line[0]]  # Change Rakevet Israel names convention to GTFS MOT stop_code
                day = calendar.day_name[datetime.strptime(line[1], '%d/%m/%Y').weekday()]  # extract day name
                line.append(day)
            else:
                line[0] = 'stop_code'  # change destination_station to stop_code
                line.append("Day")
            line = ','.join(map(str, line)) + '\n'
            text += line
    with open(output_path, 'w', encoding='utf8') as f:
        f.write(text)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', required=True)
    parser.add_argument('--dict_path', required=True)
    parser.add_argument('--output_path', required=True)
    args = parser.parse_args()
    main(data_path = args.data_path, dict_path = args.dict_path, output_path = args.output_path)