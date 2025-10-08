#!/usr/bin/env python3

# Simple SMS Command utility
#
# by Magnetic-Fox, 01.05 - 13.09.2025, 08.10.2025
#
# (C)2025 Bartłomiej "Magnetic-Fox" Węgrzyn

import sys
import subprocess
import smsSuiteConfig

def process(fromNumber, toNumber, message):
	if toNumber == "1000":
		messageParts = message.lstrip().rstrip().split(" ")
		messageParts[0] = messageParts[0].upper()

		if messageParts[0] == "HELP":
			return "Yup, this should definitely be written someday..."

		elif messageParts[0] == "UPTIME":
			return subprocess.check_output(["uptime","-p"]).decode().strip()

		elif messageParts[0] == "TEST":
			return "Number 1000 here, message from " + str(fromNumber) + ", entry: " + message

		elif messageParts[0] == "TEST2":
			return "START 12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890 END"

		return smsSuiteConfig.WRONG_COMMAND

	return smsSuiteConfig.WRONG_NUMBER

if __name__ == "__main__":
	if len(sys.argv) == 4:
		print(process(sys.argv[1], sys.argv[2], sys.argv[3]))

	else:
		print(smsSuiteConfig.WRONG_USE)
