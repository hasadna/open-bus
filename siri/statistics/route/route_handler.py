import pickle
from collections import OrderedDict
from operator import itemgetter
import pandas as pd
from jinja2 import Environment, FileSystemLoader
import pdfkit as pdf
from os import listdir
from os.path import isfile, join
import csv


def _report_trip(df, path_folder):
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
    with open('routes.html', 'w') as f:
        f.write(html_string.format(table=df.to_html(classes='mystyle')))

    # OUTPUT AN CSV FILE
    df.to_csv(open(path_folder + '\\routes.csv', 'w'), index=False)


def load_routes(path_folder):
    routes = []
    files = [f for f in listdir(path_folder) if isfile(join(path_folder, f))]
    for path in files:
        routes.extend(parse_routes(path_folder + "\\" + path))
    return routes


def handle_routes(path):
    routes = load_routes(path + "\\siri\\trips")
    # sorted_trips = sorted(trips, key=itemgetter('time_recorded'))
    df = _process_routes(routes, path)
    _report_trip(df, path + "\\siri\\routes")


def _process_routes(routes, path):
    df = pd.DataFrame(routes)
    gf = df.groupby('route_id')
    af = gf.apply(_aggregate_route)
    gtfs = pickle.load(open(path + "\\gtfs\\2017-08-23_route_stats.pkl", "rb"))
    merged_df = pd.merge(af, gtfs, left_on='route_id', right_on='route_id')
    merged_df = merged_df[
        ['route_id', 'line_num', 'agency_name', 'route_long_name', 'start_stop_id', 'end_stop_id', 'avg_total_trip', 'avg_late_start', 'avg_late_end',
         'num_trips_total','num_trips_executed', 'num_trips_skipped']]
    return merged_df


def get_sec(time_str):
    h, m = time_str.split(':')
    return int(h) * 3600 + int(m) * 60


def _aggregate_route(route_grouped):
    d = OrderedDict()
    d['route_id'] = route_grouped['route_id'].iat[0]
    d['agency_id'] = route_grouped['agency'].iat[0]
    d['line_num'] = route_grouped['line_num'].iat[0]
    d['avg_total_trip'] = "{0:.2f} min".format(route_grouped['total_trip'].replace(0, pd.np.NaN).median())
    d['avg_late_start'] = "{0:.2f} min".format(route_grouped['late_start'].loc[(route_grouped['late_start'] < 3)])
    d['avg_late_end'] = "{0:.2f} min".format(route_grouped['late_end'].mean())
    d['num_trips_total'] = route_grouped['route_id'].count()
    done_trips_sum = route_grouped['done_trip'].sum()
    done_trips_precent = done_trips_sum / d['num_trips_total'] * 100
    d['num_trips_executed'] = "{0} ({1:.2f}%)".format(done_trips_sum, done_trips_precent)
    no_trip = d['num_trips_total'] - done_trips_sum
    d['num_trips_skipped'] = "{0} ({1:.2f}%)".format(no_trip, 100 - done_trips_precent)
    # d.loc[(d.lateness > 5), 'route_id']
    return pd.Series(d)


# def _enrich_route(route_grouped):
#     d = OrderedDict()
#
#     d['Route_id'] = route_grouped['route_id'].iat[0]
#     d['Agency'] = route_grouped['agency'].iat[0]
#     d['Line_num'] = route_grouped['line_num'].iat[0]
#     d['Avg_total_trip'] = "{0:.2f} min".format(route_grouped['total_trip'].mean())
#     d['Avg_late_start'] = "{0:.2f} min".format(route_grouped['late_start'].mean())
#     d['Avg_late_end'] = "{0:.2f} min".format(route_grouped['late_end'].mean())
#     d['Number of trips'] = route_grouped['route_id'].count()
#     done_trips_sum = route_grouped['done_trip'].sum()
#     done_trips_precent = done_trips_sum / d['Number of trips'] * 100
#     d['Done trip'] = "{0} ({1:.2f}%)".format(done_trips_sum,done_trips_precent)
#     no_trip = d['Number of trips'] - done_trips_sum
#     d['No trip'] = "{0} ({1:.2f}%)".format(no_trip,100 - done_trips_precent)
#     return pd.Series(d)


def parse_routes(path):
    routes = []
    with open(path, 'r') as csvfile:
        lines = csv.reader(csvfile)
        data = [line for line in lines if line][1:]
    csvfile.close()
    for line in data:
        if type(line) == list:
            routes.append({"agency": line[0], "line_num": line[2], "route_id": line[3]
                              , "total_trip": 0 if line[7] == 'N/A' else float(line[7].split(' ', 1)[0]),
                           "late_start": 0 if line[8] == 'N/A' else float(line[8].split(' ', 1)[0]),
                           "late_end": 0 if line[9] == 'N/A' else float(line[9].split(' ', 1)[0]),
                           "done_trip": 1 if line[11].lower() == 'yes' else 0})
    return routes


if __name__ == "__main__":
    handle_routes('C:\\obus-data')
