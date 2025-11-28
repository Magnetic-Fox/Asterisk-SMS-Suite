#!/usr/bin/env python3

# Simple Asterisk call file generator
#
# by Magnetic-Fox, 19.04.2025 - 28.11.2025
#
# (C)2025 Bartłomiej "Magnetic-Fox" Węgrzyn

import subprocess
import datetime


# Asterisk call file generator function
def generateCallFile(callFileName, channel, callerID, application, data, additionalVariables = None, maxRetries = 0, retryTime = 300, waitTime = 45, archive = True):
	callFile = open(callFileName, "w")

	callFile.write("Channel: " + str(channel) + "\n")
	callFile.write("CallerID: " + str(callerID) + "\n")
	callFile.write("MaxRetries: " + str(maxRetries) + "\n")
	callFile.write("RetryTime: " + str(retryTime) + "\n")
	callFile.write("WaitTime: " + str(waitTime) + "\n")

	callFile.write("Archive: ")

	if archive:
		callFile.write("yes")
	else:
		callFile.write("no")

	callFile.write("\n")

	callFile.write("Application: " + str(application) + "\n")
	callFile.write("Data: " + str(data) + "\n")

	if additionalVariables != None:
		for additionalVariable in additionalVariables:
			callFile.write("SetVar: " + additionalVariable + "\n")

	callFile.close()

	return

# Call file moving helper
def moveCallFile(callFileName, tempDirectory = "/var/spool/asterisk/tmp", outgoingDirectory = "/var/spool/asterisk/outgoing"):
	subprocess.run(["mv", tempDirectory + "/" + callFileName, outgoingDirectory])
	return

# Simple name generation helper
def generateDateTimeName(prefix = "", postfix = "", date = None):
	if date == None:
		date = datetime.datetime.now()
	return prefix + date.strftime("%Y-%m-%d-%H-%M-%S-%f") + postfix
