#!/usr/bin/env python3

# Asterisk SMS Suite logger tools
#
# by Magnetic-Fox, 26.11.2025
#
# (C)2025 Bartłomiej "Magnetic-Fox" Węgrzyn

import logging
import logging.handlers
import smsSuiteConfig


# Global logger variable (now set for None for a while)
globalLogger = None


# Simple logger preparation function
def prepareLogger(loggerName = __name__, loggerAddress = smsSuiteConfig.LOGGER_ADDRESS):
	logger = logging.getLogger(loggerName)
	handler = logging.handlers.SysLogHandler(address = loggerAddress)

	logger.setLevel(logging.INFO)
	logger.addHandler(handler)

	return logger


# -----------------------------------------------------------------------------------------

# Prepare global logger on the module load
globalLogger = prepareLogger()

# -----------------------------------------------------------------------------------------


# Simple logging utility
def logInfo(message, prefix = "", logger = globalLogger):
	if None:
		raise Exception("No logger selected!")

	logger.info(prefix + message)

	return

# Warning logger
def logWarning(message, logger = globalLogger):
	logInfo(message, "Warning: ", logger)
	return

# Error logger
def logError(message, logger = globalLogger):
	logInfo(message, "Error: ", logger)
	return
