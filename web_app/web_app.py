
import json, urllib.request
from collections import defaultdict

print("This line will be printed.")

#18/3/2019: http://142.93.111.211:3000/trips/114 <-> http://142.93.111.211:3000/trips/167
api_url = "http://142.93.111.211:3000/trips/114"
req = urllib.request.Request(api_url)
url = urllib.request.urlopen(api_url).read()
data_from_json = json.loads(url.decode())


# regroup data
# d = defaultdict(list)
d = dict()

d["tripId"] = (data_from_json["tripId"])
d["planned_time"] = (data_from_json["planned_time"])
d["date"] = (data_from_json["date"])
d["routeId"] = (data_from_json["routeId"])
d["routeShortName"] = (data_from_json["routeShortName"])
d["routeLongName"] = (data_from_json["routeLongName"])
d["agencyName"] = (data_from_json["agencyName"])
d["routeType"] = (data_from_json["routeType"])
print(d)

# del data_from_json["stops"]
# del data_from_json["shape"]
# del data_from_json["siri"]
# data_from_json.pop('stops', None)
# data_from_json.pop('shape', None)
# data_from_json.pop('siri', None)
print(data_from_json)


def clean_data(json_object):
    del json_object["shape"]["type"]

    for element1 in json_object['stops']:
        del element1["geometry"]["type"]
        del element1["type"]
        print(element1)
    return

