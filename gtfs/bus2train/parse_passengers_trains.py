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
<< << << < HEAD
import io

train_station_to_code = """
אופקים	17109
אשדוד עד-הלום	17070
אשקלון	17072
באר-יעקב	17066
באר-שבע מרכז	17084
באר-שבע צפון	17082
בית שאן	17111
בית-יהושע	17032
בית-שמש	17074
בני ברק	17040
בנימינה	17024
בת-ים יוספטל	17052
בת-ים קוממיות	17054
דימונה	17086
הוד-השרון סוקולוב	17100
הרצלייה	17034
חדרה מערב	17028
חולון וולפסון	17050
חוצות המפרץ	17010
חיפה בת-גלים	17018
חיפה חוף-הכרמל	17020
חיפה מרכז השמונה	17016
יבנה מזרח	17068
יבנה מערב	17096
יקנעם כפר-יהושע	17110
ירושלים גן-החיות	17076
ירושלים מלחה	17078
כפר חבד	17056
כפר-סבא נורדאו	17092
לב המפרץ	17008
להבים רהט	17088
לוד	17058
לוד גני-אביב	17062
מגדל-העמק כפר-ברוך	17113
מודיעין מרכז	17002
נהרייה	17014
נתבג	17090
נתיבות	17108
נתניה	17030
נתניה ספיר	17114
עכו	17012
עפולה	17112
עתלית	17022
פאתי מודיעין	17000
פתח-תקווה סגולה	17044
צומת חולון	17048
קיסריה פרדס-חנה	17026
קריית אריה	17042
קריית חיים	17004
קריית מוצקין	17006
קריית-גת	17080
ראש-העין צפון	17094
ראשלצ הראשונים	17098
ראשלצ משה-דיין	17102
רחובות	17064
רמלה	17060
שדרות	17106
תא אוניברסיטה	17036
תא ההגנה	17104
תא השלום	17046
תא סבידור מרכז	17038
"""


def create_dict_of_stations():
    reader = csv.reader(io.StringIO(train_station_to_code), delimiter='\t')
    return {r[1]: r[0] for r in reader}


def read_data(data_path):
    station_dict = create_dict_of_stations()
    with open(data_path, 'r', encoding='utf8') as in_f:
        for line in csv.reader(in_f):
            line += [''] * (4 - len(line))  # fix missing values
            line[0] = station_dict[line[0]]  # Change Rakevet Israel names convention to GTFS MOT stop_code
            day = datetime.strptime(line[1], '%d/%m/%Y').strftime('%a')  # extract day name
            line.append(day)
            yield line


def main(data_path, output_path):
    with open(output_path, 'w', encoding='utf8') as out_f:
        writer = csv.writer(out_f)
        writer.write_row(["Station", "Date", "Hour", "PassengersCount", "Day"])
        for row in read_data(data_path):
            writer.write_row(row)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', required=True)
    parser.add_argument('--output_path', required=True)
    args = parser.parse_args()
    main(data_path=args.data_path, output_path=args.output_path)
