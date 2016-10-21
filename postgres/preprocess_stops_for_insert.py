import sys
import csv

print("Adding street, town, platform and floor to stops file")

with open(sys.argv[1], encoding='utf8') as infile, open(sys.argv[2], 'w', encoding='utf8') as outfile:
    reader = csv.DictReader(infile)
    fields = "stop_id,stop_code,stop_name,stop_desc,stop_lat,stop_lon,location_type,parent_station,zone_id".split(',')
    fields = fields + ["street", "town", "platform", "floor"]
    writer = csv.DictWriter(outfile, fieldnames=fields, lineterminator='\n')
    writer.writeheader()
    for row in reader:
        stop_desc = row['stop_desc']
        split = stop_desc.split(':')
        row['street'] = split[1][:-4].strip()
        row['town'] = split[2][:-5].strip()
        row['platform'] = split[3][:-5].strip()
        row['floor'] = split[4].strip()
        writer.writerow(row)

print("Done")