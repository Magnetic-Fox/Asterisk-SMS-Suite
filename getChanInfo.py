#!/usr/bin/env python3

# Channel information gathering utility
#
# by Magnetic-Fox, 19.04.2025 - 27.11.2025
#
# (C)2025 Bartłomiej "Magnetic-Fox" Węgrzyn

import mysql.connector
import sqlConfig


# SQL connection preparation procedure
def prepareSQLConnection():
	mydb = mysql.connector.connect(**sqlConfig.config)
	cur = mydb.cursor(buffered = True)

	return mydb, cur

# SQL connection freeing procedure
def freeSQLConnection(mydb, cur):
	if(cur != None):
		cur.close()
		cur = None

	if(mydb != None):
		mydb.close()
		mydb = None

	return

# Get extension and desired service information
def getChanInfo(number):
	mydb, cur = prepareSQLConnection()
	sql = "SELECT Extension, Message FROM PBXNumbers WHERE Account=%s"
	cur.execute(sql, (number,))
	res = cur.fetchall()
	freeSQLConnection(mydb, cur)

	try:
		return (res[0][0], res[0][1])

	except:
		return None

# Get channel information (with try and except applied)
def tryToGetChanInfo(number):
	try:
		# Get number information (extension + chosen service)
		extension, service = getChanInfo(number)

	except:
		# Set to nothing on error
		extension = ""
		service = ""

	# Return information
	return extension, service
