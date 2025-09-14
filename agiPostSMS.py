#!/usr/bin/env python3

# AGI Script for posting SIP IM as an SMS
#
# by Magnetic-Fox, 10-13.09.2025
#
# (C)2025 Bartłomiej "Magnetic-Fox" Węgrzyn

import sys
import base64
import datetime
import random
import asterisk.agi
import unidecode
import getChanInfo
import smsSuiteConfig

# Function for dividing string to substrings of chosen size
def divideString(inputString, size):
	output = []

	try:
		assert size > 0

		while len(inputString) > 0:
			output += [inputString[0:size]]
			inputString = inputString[size:]

	except:
		pass

	return output

# Function for preparing the file name and write data to the actual file
def writeSMS(path, data, da, scts, mr):
	smsFile = open(path + "/" + da + "." + scts + "-"  +mr, "w")
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

# Function for communicating with Asterisk via AGI - receive and process message
def AGI_getAndPostSMS():
	agi = asterisk.agi.AGI()

	try:
		if (len(sys.argv) == 2) and (sys.argv[1] == "SMS"):
			oa = agi.get_variable("SMS_OA")
			da = agi.get_variable("SMS_DA")

		else:
			oa = agi.get_variable("MESSAGE(from)")
			oa = oa[oa.find("sip:") + 4:oa.find("@")]

			da = agi.get_variable("EXTEN")

		# asterisk.agi library doesn't like new lines, so thanks God
		# Asterisk has Base64 encoding utility (which we have to decode now)...
		ud = base64.b64decode(agi.get_variable("MSG_B64").encode("utf8")).decode("utf8")

		ud = ud.replace("\r\n", "\n")
		ud = ud.replace("\n", " ")

		ud = ud.lstrip().rstrip()

		# If sending SMS - get rid of any UTF-8 accents and divide into 160-character-sized messages...
		if getChanInfo.getChanInfo(da)[1] == "S":
			ud = unidecode.unidecode(ud)
			ud = divideString(ud, 160)

		else:
			# Simple workaround for code below
			ud = [ud]

		# Post all messages
		for s_ud in ud:
			# Let's use current date and random reference number for the message
			scts = str(datetime.datetime.now().replace(microsecond = 0).isoformat())
			mr = str(random.randrange(0, 255, 1))

			writeSMS(smsSuiteConfig.AST_SMS_SPOOL, prepareSMS(oa, da, s_ud, scts, mr), da, scts, mr)

		return 0

	except:
		return 1

	return 0

# Autorun section
if __name__ == "__main__":
	exit(AGI_getAndPostSMS())
