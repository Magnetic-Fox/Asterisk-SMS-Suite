#!/usr/bin/env python3

# Some SMS tools
#
# by Magnetic-Fox, 17.04.2025 - 26.11.2025
#
# (C)2025 Bartłomiej "Magnetic-Fox" Węgrzyn

import subprocess
import configparser


# SMS sending utility
def sendSMS(smsCentreSending, toExtension, fromNumber, message, dateTime = None, messageReference = None, queue = None, userDataHeader = None, noDial = False):
	smsqCommand = [	"smsq",
			"--mt",
			"--tx",
			"--mttx-callerid=" + str(smsCentreSending),
			"--mttx-channel=" + str(toExtension),
			"--oa=" + str(fromNumber),
			"--ud=" + str(message)	]

	if dateTime != None:
		smsqCommand += ["--scts=" + str(dateTime)]

	if messageReference != None:
		smsqCommand += ["--mr=" + str(messageReference)]

	if queue != None:
		smsqCommand += ["--queue=" + str(queue)]

	if userDataHeader != None:
		smsqCommand += ["--udh=" + str(userDataHeader)]

	if noDial:
		smsqCommand += ["--no-dial"]

	subprocess.run(smsqCommand)

	return

# Message contents extractor
def getMessageContents(messageFilePath):
	parser = configparser.ConfigParser(interpolation = None)
	message = open(messageFilePath, "r")
	parser.read_string("[SMS]\n" + message.read())
	message.close()

	return parser.get("SMS", "oa"), parser.get("SMS", "da"), parser.get("SMS", "ud"), parser.get("SMS", "scts"), parser.getint("SMS", "mr")
