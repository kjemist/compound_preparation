#!/usr/bin/python

#load smiles in table, check that identifier exists


import string,os, sys
import my_mysql as mysql
import MySQLdb

if len(sys.argv) <> 5:
	print 'mysql_load_filter_des.py  <username> <password> <data file> <project>'
	sys.exit(1)

username = sys.argv[1]
password = sys.argv[2]
data_file = open(sys.argv[3], 'r')
project = sys.argv[4]

#-------------------------------------
#-------------------------------------
conn=mysql.connect2server(password, username,'purchasable')  			  
			  
cursor = conn.cursor ()


#get table names

command = 'select unique_compounds from projects where project = "' + project + '"'
print command
cursor.execute(command)
results=cursor.fetchall()
if len(results) == 0:
	print 'project does not exist'
	sys.exit(1)

table = results[0][0]

#get id,
command = "show fields from " + table
cursor.execute(command)
results=cursor.fetchall()
for result in results:
	if result[3] == 'PRI':
		id_field = result[0]


#read first line of input data => is header
header = data_file.readline()

field_dict = {}
ordered_list = []

header = header.strip()
header = header.replace('identifier', id_field)
split_header = header.split('\t')

for i in range(0, len(split_header)):
	field_dict[split_header[i]]= i
	ordered_list.append(split_header[i])


print "insert data"


for i in data_file.xreadlines():
     i = i.replace('False', 'n')
     i = i.replace('True', 'y')
     list = []
     start = 0
     for j in range(0,i.count('\t')):
       end = i.find('\t',start)
       value = string.strip(i[start:end])
       list.append(value)
       start = end + 1
     list.append(string.strip(i[start:]))
     
     #remove leading characters from label
     if list[0][0] == 'P':
	list[0] = list[0][1:]
	
     #print list
     #make sure that label exits
     command = 'SELECT ' + id_field + ' FROM ' + table + ' WHERE ' + id_field+ ' = "' + list[field_dict[id_field]] + '"'
     #print command    
     cursor.execute(command)
     label_exists = cursor.fetchall ()
     if len(label_exists) == 1 :
	     command = 'update ' + table + ' set '
     	     for field in ordered_list:
		if field <> id_field:
			command = command + field + "= '" + list[field_dict[field]] + "', " 
     	     command = command[:-2] + ' where ' + id_field + ' = ' +  list[field_dict[id_field]]
		
     	     #print command
     	     cursor.execute(command)
  
     else:
	print list[field_dict[id_field]] + 'does not exist'

  
 
print 'finished upload'  
cursor.close ()
conn.commit()
conn.close ()
