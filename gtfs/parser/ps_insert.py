#!/usr/bin/env python
# -*- coding: utf-8 -*-
import psycopg2
import os
from jinja2 import Environment, FileSystemLoader
import os.path
import unicodecsv
import sys
reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF8')




DATA_DIR = "../data"
TEMPLATES_PATH = '../templates'

#data files
CONNECTION_DATA_FILE = "connection_details.txt"
MAPPING_FILE = "mapping.txt"

#template files
CONNECTION_TEMPLATE_FILE_NAME = "ps_connection_string.template"
QUERY_TEMPLATE_FILE_NAME = "ps_query.template"

'''
build connection string from data and template
'''
def build_connection_string(data_file,conn_template):
	data = {}
	with open(data_file,'r') as f:
		for line in f.readlines():
			data[line.split(' ')[0]]=line.split(' ')[1]

	return conn_template.render(data=data)
	conn_obj =connect()


'''
given a connection string creates connection to ps db
'''
def connect(conn_string):
    try:
        return psycopg2.connect(conn_string)
    except psycopg2.Error as e:
        print ("Unable to connect to database. {}".format(e))


'''
return tablename and list object of tuples 
of column name and data type 
'''
def get_columns(file_path,mapping_file):
	table_name = os.path.splitext(os.path.basename(file_path))[0]
	columns = []
	with open(mapping_file,'r') as f:
		line = ""
		while line.strip()!="TABLE "+table_name:
			line = f.readline()

		while line!=None:
		
			line = f.readline()
			line_arr = line.split(" ")
			if len(line_arr)<2:
				break
			columns.append((line_arr[0],line_arr[1]))
	
	return table_name ,columns

'''
file path - the path of the file containing data, notice - the name
of the file must match to the table e.g. egency.txt to table agency
conn_obj - connection object to postgres received in connect method
mapping file - a file containing tables and their columns as present
in the db
query template - template for queries in postgres

'''
def insert_file_to_db(file_path,cursor,mapping_file,query_template):
	table_name,columns = get_columns(file_path,mapping_file)

	with open(file_path,'r') as f:
		#find indices of columns in the postgres actual table
		reader = unicodecsv.DictReader(f,encoding='utf-8')
		for row in reader:
			print row
			values = []
			placeholder = []
			for col in columns:
			
				values.append(row[col[0]])
				placeholder.append("%s")

	

			query = query_template.render(columns=zip(*columns)[0]\
				,values=placeholder,table_name=table_name)
			print query
			cursor.execute(query,values)
			



def insert_folder_to_db(folder):
	env = Environment(loader=FileSystemLoader(TEMPLATES_PATH))

	conn_template = env.get_template(CONNECTION_TEMPLATE_FILE_NAME)


	conn_obj =connect(build_connection_string(\
		os.path.join(DATA_DIR,CONNECTION_DATA_FILE),\
		conn_template))

	cursor= conn_obj.cursor()

	query_template = env.get_template(QUERY_TEMPLATE_FILE_NAME)

	for file in os.listdir(folder):
		print file
		# try:
		insert_file_to_db(os.path.join(folder,file),\
		cursor,os.path.join(DATA_DIR,MAPPING_FILE),\
		query_template)
		# except Exception as e:
		# 	print file + " failed"
		# 	print e.message


	conn_obj.close()

insert_folder_to_db("../sample/pub")