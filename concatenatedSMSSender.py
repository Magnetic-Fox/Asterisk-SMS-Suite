#!/usr/bin/env python3

# Concatenated SMS sender utility (utilizing smsq)
#
# by Magnetic-Fox, 26.04 - 08.10.2025
#
# (C)2025 Bartłomiej "Magnetic-Fox" Węgrzyn

import sys
import subprocess
import datetime
import random

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
		if messageReference == "XPARAM_NONE":
			# Make it random on "None"
			messageReference = random.randrange(0, 255, 1)
		else:
			messageReference = int(messageReference)

		command = ["smsq", "--mt", "--tx", "--mttx-callerid=" + str(callerID), "--mttx-channel=" + extension, "--oa=" + str(originator), "--mr=" + str(messageReference), "--queue=" + str(queue)]

		if scts != "XPARAM_NONE":
			command += ["--scts=" + scts]

		if len(message) <= 160:
			command += ["--ud=" + message]
			subprocess.check_output(command)

		else:
			if messageReference < 256:
				messages = splitMessage(message, 153)

			else:
				# for messages with 16-bit reference code there is even lower space left for one message
				messages = splitMessage(message, 152)

			for x in range(len(messages)):
				userDataHeader = generateUserDataHeader(messageReference, len(messages), x + 1)

				if x + 1 < len(messages):
					subprocess.check_output(command + ["--udh=" + userDataHeader, "--ud=" + messages[x], "--no-dial"])
				else:
					# Post call file only while creating last part of message
					subprocess.check_output(command + ["--udh=" + userDataHeader, "--ud=" + messages[x]])

	except Exception as e:
		return 1

	return 0

# Autorun part
if __name__ == "__main__":
	if len(sys.argv) == 8:
		# Just run everything and return proper exit code
		exit(sendConcatenatedMessage(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7]))
	else:
		exit(1)
