import psycopg2

class database_fixture(self):
	def connect_to_database(self, database_name)
		try:
			conn = psycopg2.connect("dbname=dataBaseName user='postgress' host='localhost' password='dbpass'")
		except:
			print "Unable to connect database: "+database_name+" YELP!"
		print "connection succeed."
		return conn
			
	def insert_multi_arrival_rows(self, bus_arrival, database_name =  'openbus30bus'):
		print "inserting row"
		curruntDB = self.connectToDatabase(database_name)
		for item in bus_arrival:
			print "insert rows"
	
		

		