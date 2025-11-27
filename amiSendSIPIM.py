#!/usr/bin/env python3

# Simple Asterisk's AMI sending SIP IM utility
#
# by Magnetic-Fox, 13.09.2025 - 27.11.2025
#
# (C)2025 Bartłomiej "Magnetic-Fox" Węgrzyn

import base64
import asterisk.manager
import amiConfig


# AMI SIP message sending utility
def sendMessage(msgFrom, msgTo, message):
	try:
		# Create AMI object and login
		ami = asterisk.manager.Manager()
		ami.connect(amiConfig.ADDRESS)
		ami.login(amiConfig.SIPIM_USERNAME, amiConfig.SIPIM_PASSWORD)

		# Prepare action data (message to send)
		action = {"Action": "MessageSend",
			"From": str(msgFrom),
			"To": "sip:"+str(msgTo),
			"Base64Body": base64.b64encode(message.encode("utf8")).decode("utf8")}

		# Send action to Asterisk and logout
		response = ami.send_action(action)
		ami.logoff()

		# Return information according to the response from Asterisk
		if response["Response"] == "Success":
			return 0
		elif response["Response"] == "Error":
			return 1
		else:
			return 2

	except:
		# Non-zero return on error (obviously)
		return 2

	# Return 0 at the end (function should stop before, but I've added it for additional safety)
	return 0
