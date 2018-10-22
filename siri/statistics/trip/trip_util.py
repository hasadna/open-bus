def prepare_trip_example():
    trip = []
    a = '3, 10394, 7, 33621616, 18: 15, 8727501, 18: 54, 18: 15:01, 31.738306045532227, 35.219261169433594'
    with open('trip_example.txt') as f:
        data = f.readlines()
    f.close()
    for line in data:
        trip_input = line.strip().split(',')
        trip.append({"agency": trip_input[0], "route_id": trip_input[1], "line_num": trip_input[2]
        , "service_id": trip_input[3], "start_time": trip_input[4], "bus_id": trip_input[5],
           "end_time": trip_input[6], "time_recorded": trip_input[7], "coordinates": {trip_input[8], trip_input[9]}})

    return trip


def get_sec(time_str):
    h, m = time_str.split(':')
    return int(h) * 3600 + int(m) * 60