#!/usr/bin/env python3

# Simple SMS Command utility (simple experiment - do not take really seriously)
#
# by Magnetic-Fox, 01.05 - 14.09.2025
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
			return "No tak, przydaloby sie kiedys napisac pomoc..."

		elif messageParts[0] == "UPTIME":
			return subprocess.check_output(["uptime","-p"]).decode().strip()

		elif messageParts[0] == "TEST":
			return "Numer 1000, wiadomosc od " + str(fromNumber) + ", tresc: " + message

		return smsSuiteConfig.WRONG_COMMAND

	return smsSuiteConfig.WRONG_NUMBER

if __name__ == "__main__":
	if len(sys.argv) == 4:
		print(process(sys.argv[1], sys.argv[2], sys.argv[3]))

	else:
		print(smsSuiteConfig.WRONG_USE)
