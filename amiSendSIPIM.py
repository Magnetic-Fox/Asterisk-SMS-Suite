#!/usr/bin/env python3

# Simple Asterisk's AMI sending SIP IM utility
#
# by Magnetic-Fox, 13.09.2025
#
# (C)2025 Bartłomiej "Magnetic-Fox" Węgrzyn

import sys
import base64
import asterisk.manager
import amiConfig

def sendMessage(msgFrom, msgTo, message):
	try:
		ami = asterisk.manager.Manager()
		ami.connect(amiConfig.ADDRESS)
		ami.login(amiConfig.SIPIM_USERNAME, amiConfig.SIPIM_PASSWORD)

		action = {"Action": "MessageSend",
			"From": str(msgFrom),
			"To": "sip:"+str(msgTo),
			"Base64Body": base64.b64encode(message.encode("utf8")).decode("utf8")}

		response = ami.send_action(action)
		ami.logoff()

		if response["Response"] == "Success":
			return 0
		elif response["Response"] == "Error":
			return 1
		else:
			return 2

	except:
		return 2

	return 0

if __name__ == "__main__":
	sys.exit(sendMessage(sys.argv[1], sys.argv[2], sys.argv[3]))
