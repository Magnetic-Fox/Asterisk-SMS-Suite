#!/usr/bin/env python3

# Concatenated SMS sender utility (utilizing smsq)
#
# by Magnetic-Fox, 26.04.2025 - 26.11.2025
#
# (C)2025 Bartłomiej "Magnetic-Fox" Węgrzyn

import random
import smsTools


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
			smsTools.sendSMS(callerID, extension, originator, message, scts, messageReference, queue)

		else:
			if messageReference < 256:
				messages = splitMessage(message, 153)

			else:
				# for messages with 16-bit reference code there is even lower space left for one message
				messages = splitMessage(message, 152)

			for x in range(len(messages)):
				userDataHeader = generateUserDataHeader(messageReference, len(messages), x + 1)

				if x + 1 < len(messages):
					smsTools.sendSMS(callerID, extension, originator, messages[x], scts, messageReference, queue, userDataHeader, True)

				else:
					# Post call file only while creating last part of message
					smsTools.sendSMS(callerID, extension, originator, messages[x], scts, messageReference, queue, userDataHeader)

	except:
		return False

	return True
