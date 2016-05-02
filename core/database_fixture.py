import psycopg2

class database_fixture(self):
	def connect_to_database(self, database_name)
		try:
			conn = psycopg2.connect("dbname=dataBaseName user='postgres' host='localhost' password='dbpass'")
		except:
			print "Unable to connect database: "+database_name+" YELP!"
		print "connection succeed."
		return conn
		
			
	def insert_multi_arrival_rows(self, bus_arrival, database_name =  'openbus30bus'):
		print "inserting row"
		curr = self.connectToDatabase(database_name).cursor()
		for item in bus_arrival:
			print "insert rows"
			insert =  "INSERT INTO buses (uniqline, line_ref, direction_ref, published_line_name, operator_ref, destination_ref, monitoring_ref, expected_arrival_time, stop_point_ref, node_start, response_key, node_end) VALUES (%d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d);"
			data = (0, item.line_ref, item.direction_ref, item.published_line_name, item.operator_ref, item.destination_ref, item.monitoring_ref, item.expected_arrival_time, item.stop_point_ref, 0, 0, 0)
			curr.execute(insert, data)
			
	