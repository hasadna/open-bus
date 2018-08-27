from collections import OrderedDict
from operator import itemgetter
import pandas as pd
from jinja2 import Environment, FileSystemLoader
import pdfkit as pdf


def _report_trip(df):
    # env = Environment(loader=FileSystemLoader('.'))
    # template = env.get_template("trip_report.html")
    # template_vars = {"title": "Trips Report",
    #                  "trips_table": df.to_html()}
    # html_out = template.render(template_vars)
    # pdf.from_file('trip_report.html', 'report.pdf')
    pd.set_option('colheader_justify', 'center')  # FOR TABLE <th>
    pd.set_option('display.width', 1000)
    html_string = '''
    <html>
      <head><title>HTML Pandas Dataframe with CSS</title></head>
      <link rel="stylesheet" type="text/css" href="df_style.css"/>
      <body>
        {table}
      </body>
    </html>.
    '''

    # OUTPUT AN HTML FILE
    with open('report.html', 'w') as f:
        f.write(html_string.format(table=df.to_html(classes='mystyle')))

    # OUTPUT AN CSV FILE
    df.to_csv(open('report.csv', 'w'), index=False)


def handle_trips(path):
    trips = parse_trips(path)
    sorted_trips = sorted(trips, key=itemgetter('time_recorded'))
    df = _process_trips(sorted_trips)
    _report_trip(df)


def _process_trips(trips):
    df = pd.DataFrame(trips)
    gf = df.groupby('service_id')

    return gf.apply(_aggregate_trip)


def get_sec(time_str):
    h, m = time_str.split(':')
    return int(h) * 3600 + int(m) * 60


def _aggregate_trip(trip_grouped):
    d = OrderedDict()
    d['agency'] = trip_grouped['agency'].iat[0]
    d['bus_id'] = trip_grouped['bus_id'].iat[0]
    d['line_num'] = trip_grouped['line_num'].iat[0]
    d['route_id'] = trip_grouped['route_id'].iat[0]
    d['service_id'] = trip_grouped['service_id'].iat[0]
    d['start_time'] = trip_grouped['start_time'].iat[0]
    d['end_time'] = trip_grouped['end_time'].iat[-1]
    end_location = trip_grouped['coordinates'].iat[-1]
    is_active = False
    if float(end_location[0]) > 0 or float(end_location[1]):
        is_active = True
    d['total_trip_time'] = str(
        (get_sec(d['end_time']) - get_sec(d['start_time'])) / 60) + ' min' if is_active else 'N/A'
    coord = (0, 0)
    index_coord = 0
    for i, coord in enumerate(trip_grouped['coordinates']):
        if float(coord[0]) > 0 or float(coord[1]) > 0:
            coord = (coord[0], coord[1])
            index_coord = i
            break
    time_recorded = trip_grouped['time_recorded'].iat[index_coord].split(':')[:-1]
    d['late_start'] = str(abs(get_sec(':'.join(time_recorded)) - get_sec(
        trip_grouped['start_time'].iat[0])) / 60) + ' min' if is_active else 'N/A'
    d['late_end'] = str(
        abs(get_sec(trip_grouped['end_time'].iat[-1]) - get_sec(
            trip_grouped['end_time'].iat[0])) / 60) + ' min' if is_active else 'N/A'
    d['done_trip'] = 'Yes' if is_active else 'No'
    d['start_location'] = coord
    d['end_location'] = trip_grouped['coordinates'].iat[-1]

    return pd.Series(d)


def parse_trips(path):
    trip = []
    with open(path, 'rb') as f:
        lines = f.read().strip().splitlines()
        data = [line.split(b',')[2:] for line in lines if line]
    f.close()
    for line in data:
        line = [element.decode("utf-8") for element in line]
        trip.append({"agency": line[0], "route_id": line[1], "line_num": line[2]
                        , "service_id": line[3], "start_time": line[4], "bus_id": line[5],
                     "end_time": line[6], "time_recorded": line[7],
                     "coordinates": (line[8], line[9])})

    return trip


def prepare_trip_example():
    trip = []
    with open('trip_example.txt') as f:
        data = f.readlines()
    f.close()
    for line in data:
        trip_input = line.strip().split(',')
        trip.append({"agency": trip_input[0], "route_id": trip_input[1], "line_num": trip_input[2]
                        , "service_id": trip_input[3], "start_time": trip_input[4], "bus_id": trip_input[5],
                     "end_time": trip_input[6], "time_recorded": trip_input[7],
                     "coordinates": (trip_input[8], trip_input[9])})

    return trip


if __name__ == "__main__":
    handle_trips('siri_rt_data.log')
