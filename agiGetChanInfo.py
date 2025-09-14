#!/usr/bin/env python3

# Simple gathering channel information wrapper for Asterisk's AGI
#
# by Magnetic-Fox, 10-11.09.2025
#
# (C)2025 Bartłomiej "Magnetic-Fox" Węgrzyn

import sys
import asterisk.agi
import getChanInfo

def AGI_GetChanInfo():
	agi = asterisk.agi.AGI()

	try:
		if len(sys.argv) == 2:
			channelInfo = getChanInfo.getChanInfo(agi.get_variable(sys.argv[1]))
		else:
			channelInfo = getChanInfo.getChanInfo(agi.get_variable("EXTEN"))

		if channelInfo == None:
			# Let's say "U" simply means UNKNOWN
			agi.set_variable("MSG_CHAN_OPT", "U")
		else:
			agi.set_variable("MSG_CHAN_OPT", channelInfo[1])

	except:
		# Let's say "N" will be used on internal error (NO MESSAGES)
		agi.set_variable("MSG_CHAN_OPT", "N")

	return

# Autorun section
if __name__ == "__main__":
	AGI_GetChanInfo()
