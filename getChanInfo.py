#!/usr/bin/env python3

# Channel information gathering utility
#
# by Magnetic-Fox, 19-20.04.2025, 07.09.2025
#
# (C)2025 Bartłomiej "Magnetic-Fox" Węgrzyn

# Import section
import sys
import mysql.connector
import sqlConfig

# Some globals
mydb = None
cur = None

# SQL connection preparation procedure
def prepareSQLConnection():
	global mydb, cur

	if mydb == None:
		mydb = mysql.connector.connect(**sqlConfig.config)

	if cur == None:
		cur = mydb.cursor(buffered = True)

	return

# SQL connection freeing procedure
def freeSQLConnection():
	global mydb, cur

	if(cur != None):
		cur.close()
		cur = None

	if(mydb != None):
		mydb.close()
		mydb = None

	return

# Get extension and desired service information
def getChanInfo(number):
	global mydb, cur

	prepareSQLConnection()
	sql = "SELECT Extension, Message FROM PBXNumbers WHERE Account=%s"
	cur.execute(sql, (number,))
	res = cur.fetchall()
	freeSQLConnection()

	try:
		return (res[0][0], res[0][1])

	except:
		return None

# Autorun
if __name__ == "__main__":
	if len(sys.argv) > 1:
		resp = getChanInfo(sys.argv[1])

		if(resp != None):
			print(resp[0])
			print(resp[1])
			exit(0)

		else:
			exit(1)

	else:
		exit(1)
