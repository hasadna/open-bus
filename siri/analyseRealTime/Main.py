#!/usr/bin/python3

import datetime
import sys
import Cruds
import ConfigFileParser
import logging


logger = logging.getLogger()
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')

fileHandler = logging.FileHandler('log.txt')
fileHandler.setFormatter(formatter)
fileHandler.setLevel(logging.NOTSET)

stdoutHandler = logging.StreamHandler()
stdoutHandler.setFormatter(formatter)
stdoutHandler.setLevel(logging.DEBUG)


logger.addHandler(stdoutHandler)
logger.addHandler(fileHandler)


logger.warning('often makes a very good meal of %s', 'visiting tourists')

configs = ConfigFileParser.wrapper(sys.argv)

connection = configs['connection']
date = datetime.datetime.strptime(configs['date'],"%Y-%m-%d").date()


with Cruds.Connection(**connection) as c:
    trips = Cruds.CrudPostgresql(c).get_relevant_trips_from_gtfs(date)

    for trip in trips:
        try:
            results = trip.run()
            print("Trip_id: {} trip_date: {} results: {} len errores: {}".format(trip.trip_id, trip.trip_date, results.get('num of real times'), len(results.get('errors'))))
        except Cruds.InvalidDbState as e:
            #print("P")
            logging.warning("{}".format(*e.args))
        except Exception as e:
            raise Exception
