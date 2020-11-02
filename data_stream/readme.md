# Data Stream initiative
This initiative try to achieve a data flow that include: 
1. Parsing Siri log
2. Add analytical information on each ride
3. store the information on persistence document database as mongo-db

## Demo

``` 
from data_stream.data_access_layer import SiriRideMongoCrud, MongoCrud
from data_stream.siri_log_parser import InMemoryRidesCacheMechanism, SiriLogParser

log_parser = SiriLogParser(InMemoryRidesCacheMechanism())
        log_parser.parse_multi_gz_files([r'..\..\data\siri_rt_data_v2.2020-06-25.1.log.gz',
                                         r'..\..\data\siri_rt_data_v2.2020-06-25.2.log.gz'])

        crud = SiriRideMongoCrud(MongoCrud(MongoClient(), 'test_db'))
        for ride in log_parser.get_rides():
            crud.create(ride)
```
