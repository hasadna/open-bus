import os
import calendar

import partridge as ptg

from gtfs_utils import get_cluster_to_line_df, get_ftp_file


FILES_DIR = "/tmp/openbus"
CLUSTER_FILE = "ClusterToLine.zip"
GTFS_FILE = "gtfs.zip"

CITY = "עירוני"
INTER_CITY = "אזורי"
LOCAL = "בינעירוני"


class UnknownRouteType(Exception):
    pass


def main():
    os.makedirs(FILES_DIR, exist_ok=True)
    path = os.path.join(FILES_DIR, CLUSTER_FILE)
    try:
        get_ftp_file(file_name=CLUSTER_FILE, local_path=path)
    except FileExistsError:
        pass

    pd_cluster = get_cluster_to_line_df(path)
    clusters = pd_cluster.groupby(by="route_type_desc")

    print(clusters.size())

    path = os.path.join(FILES_DIR, GTFS_FILE)
    try:
        get_ftp_file(local_path=path)
    except FileExistsError:
        pass

    pd = ptg.feed(path)

    trips_data = pd.trips.merge(pd.routes, on='route_id').merge(pd.calendar, on='service_id')

    print("Trips count per day:")
    for day in calendar.day_name:
        print(f"{day}: {len(trips_data[trips_data[day.lower()] == 1])}")

    trips_data['short_route_desc'] = trips_data['route_desc'].map(lambda x: str(x).split("-")[0])
    pd_cluster['short_route_desc'] = pd_cluster['route_id'].map(lambda x: str(x))
    trips_data = trips_data.merge(pd_cluster, on='short_route_desc')
    print("Trips count per day by cluster:")
    for day in calendar.day_name:
        print(f"{day}:")
        for route_type in [CITY, INTER_CITY, LOCAL]:
            print(f"    {route_type}: "
                  f"{len(trips_data[(trips_data[day.lower()] == 1) & (trips_data['route_type_desc'] == route_type)])}")


if __name__ == '__main__':
    main()
