#!/usr/bin/env python3

# SMS tools (with support for concatenated messages)
#
# by Magnetic-Fox, 17.04.2025 - 02.01.2026
#
# (C)2025-2026 Bartłomiej "Magnetic-Fox" Węgrzyn

import random
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

# Simple message splitter (to chosen length)
def splitMessage(message, length):
	output = []

	while(len(message) > 0):
		output += [message[0:length]]
		message = message[length:]

	return output

# Simple 2- or 4-digit hex from ordinary int generator
def generate2or4Hex(int):
	hexOutput = f'{(int%65536):x}'.upper()

	if ((int % 65536) < 16) or (((int % 65536) > 255) and ((int % 65536) < 4096)):
		return '0' + hexOutput
	else:
		return hexOutput

# User Data Header for concatenated SMS generator
def generateUserDataHeader(messageReference, splitsCount, splitIndex):
	messageReference = generate2or4Hex(messageReference)

	if len(messageReference) == 2:
		# for 8-bit message reference code (00 03 MR SC SI)
		return '0003' + messageReference + generate2or4Hex(splitsCount) + generate2or4Hex(splitIndex)
	else:
		# for 16-bit message reference code (08 04 MR MR SC SI)
		return '0804' + messageReference + generate2or4Hex(splitsCount) + generate2or4Hex(splitIndex)

# Message sender utility (normal or concatenated depending on its length and messageReference width)
def sendConcatenatedMessage(callerID, extension, originator, message, scts, messageReference, queue):
	try:
		if messageReference == None:
			# Make it random on None
			messageReference = random.randrange(0, 255, 1)
		else:
			messageReference = int(messageReference)

		if len(message) <= 160:
			# For messages up to 160 characters long, send normal SMS (non-concatenated)
			sendSMS(callerID, extension, originator, message, scts, messageReference, queue)

		else:
			if messageReference < 256:
				messages = splitMessage(message, 153)

			else:
				# for messages with 16-bit reference code there is even lower space left for one message
				messages = splitMessage(message, 152)

			for x in range(len(messages)):
				userDataHeader = generateUserDataHeader(messageReference, len(messages), x + 1)

				if x + 1 < len(messages):
					sendSMS(callerID, extension, originator, messages[x], scts, messageReference, queue, userDataHeader, True)

				else:
					# Post call file only while creating last part of message
					sendSMS(callerID, extension, originator, messages[x], scts, messageReference, queue, userDataHeader)

	except:
		return False

	return True

# Explicit wrapper for sending regular or concatenated SMS
def sendProperSMS(smsCentreSendingNumber, toExtension, source, message, dateTime, messageReference, queue, useConcatenation = True):
	if useConcatenation and len(message) > 160:
		sendConcatenatedMessage(smsCentreSendingNumber, toExtension, source, message, dateTime, messageReference, queue)
	else:
		sendSMS(smsCentreSendingNumber, toExtension, source, message, dateTime, messageReference, queue)

	return

# Function for preparing the file name and write data to the actual file
def writeSMS(path, data, da, scts, mr):
	smsFile = open(path + "/" + da + "." + scts + "-" + mr, "w")
	smsFile.write(data)
	smsFile.close()

	return

# Function for preparing data for the SMS file
def prepareSMS(oa, da, ud, scts, mr):
	output = "oa=" + oa + "\n"
	output += "da=" + da + "\n"
	output += "ud=" + ud + "\n"
	output += "scts=" + scts + "\n"
	output += "mr=" + mr

	return output
