#!/usr/bin/env python3

# Simple SMS Command utility
#
# by Magnetic-Fox, 01.05.2025 - 26.11.2025
#
# (C)2025 Bartłomiej "Magnetic-Fox" Węgrzyn

import subprocess
import smsSuiteConfig


def process(fromNumber, toNumber, message):
	if toNumber == "1000":
		messageParts = message.lstrip().rstrip().split(" ")
		messageParts[0] = messageParts[0].upper()

		if messageParts[0] == "HELP":
			return "Yup, this should definitely be written someday..."

		elif messageParts[0] == "UPTIME":
			return subprocess.run(["uptime","-p"], capture_output = True).stdout.decode().strip()

		elif messageParts[0] == "TEST":
			return "Number 1000 here, message from " + str(fromNumber) + ", entry: " + message

		elif messageParts[0] == "TEST2":
			return "START 12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890 END"

		return smsSuiteConfig.WRONG_COMMAND

	return smsSuiteConfig.WRONG_NUMBER
