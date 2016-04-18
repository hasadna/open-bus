import sqlite3
import sys

# Written by:
#   yehuda nurieli - kv100100@gmail.com
#   Rafi Gana      - rafig93@gmail.com
# Written for "the public knowledge workshop"
# Non-commercial use only


def exec_sql_query(query):
	conn = sqlite3.connect("static.db")
	c = conn.cursor()

	c.execute(query)

	conn.commit()
	conn.close()

def insert_to_db(table_name, columns, entries):
	conn = sqlite3.connect("static.db")
	c = conn.cursor()

	columns = """ (""" + ','.join([column for column in columns]) + """) values """ 
	print(columns)
	query = "insert into {table_name} {columns}".format(table_name=table_name, columns=columns)
	
	

	values = ""
	for entry in entries:
		datarow=""
		for col in entry:
			datarow += ',"{}"'.format(col)
		exec_query = "{query} ({values});".format(query=query, values=datarow[1:])
		# print(exec_query)
		# sys.exit()
		c.execute(exec_query)

	conn.commit()
	conn.close()

	print("table {} db close".format(table_name))

def make_index(table_name, column_names=None):
	query = str("""CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}"""
		.format(index_name=table_name +'_ind',table_name=table_name))

	if column_names is not None:
		column_names = ",".join(column_names)
		query += "({})".format(column_names)

	query+=' ;'
	print(query)
	exec_sql_query(query)



def make_schema(table_name, columns):
	query =  str("""create table  IF NOT EXISTS  {} (""" + ','.join([column +' VARCHAR(120) ' for column in columns]) + """);""").format(table_name)
	print(query)
	exec_sql_query(query)


def select(query):
	conn = sqlite3.connect("static.db")
	return conn.execute(query)