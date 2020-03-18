import json, urllib.request, time
from collections import defaultdict
from datetime import datetime

dict_output = defaultdict(lambda: defaultdict(int))
lateness_interval = 300 #seconds


def clean_data(json_object):
    del json_object["shape"]["type"]

    for element1 in json_object['stops']:
        del element1["geometry"]["type"]
        del element1["type"]
        print(element1)
    return


def open_json(url):
    url = urllib.request.urlopen(url).read()
    data_from_json = json.loads(url.decode())
    return data_from_json


def check_depart_on_time(json_object):
    p = '%H:%M:%S'
    epoch = datetime(1970, 1, 1)

    planned_time = (data_from_json["planned_time"])
    # print(planned_time)
    planned_time_epoch = (datetime.strptime(planned_time, p) - epoch).total_seconds()
    # print(planned_time_epoch)

    try:
        time_recorded = (data_from_json["siri"]["features"][0]["properties"]["time_recorded"])
    except IndexError:
        return None
    # print(time_recorded)
    time_recorded_epoch = (datetime.strptime(time_recorded, p) - epoch).total_seconds()
    # print(time_recorded_epoch)
    seconds_elapsed = abs(planned_time_epoch - time_recorded_epoch)
    # print(seconds_elapsed)

    return lateness_interval > seconds_elapsed


if __name__ == '__main__':
    #18/3/2019: http://142.93.111.211:3000/trips/114 <-> http://142.93.111.211:3000/trips/167
    #total entries: http://142.93.111.211:3000/trips/0 <-> http://142.93.111.211:3000/trips/1329
    for i in range(1330):
        api_url = "http://142.93.111.211:3000/trips/"+str(i)
        print("checking: " + api_url)

        data_from_json = open_json(api_url)
        ride_on_time = check_depart_on_time(data_from_json)
        ride_date = data_from_json["date"]
        if ride_on_time is not None:
            dict_output[ride_date]["ride_on_time"] += ride_on_time
            dict_output[ride_date]["number_of_rides"] += 1
        else:
            print("ERROR: problem with data on "+api_url)

    # print(dict_output)
    json.dump(dict_output, open('results.json', 'w', encoding="utf8"), ensure_ascii=False)
