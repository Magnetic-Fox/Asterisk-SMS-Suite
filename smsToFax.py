#!/usr/bin/env python3

# Simple SMS to Fax relay
#
# by Magnetic-Fox, 19.04.2025 - 25.11.2025
#
# (C)2025 Bartłomiej "Magnetic-Fox" Węgrzyn

import subprocess
import tempfile
import sys
import os
import datetime
import cutter
import tiffTools
import callFileGenerator
import smsSuiteConfig


# Simple name generation helper
def generateDateTimeName(prefix = "", postfix = "", date = None):
	if date == None:
		date = datetime.datetime.now()
	return prefix + date.strftime("%Y-%m-%d-%H-%M-%S-%f") + postfix

# Simple error logging utility...
def logError(errorString):
        subprocess.run(["logger", errorString])
        return

# Asterisk call file creation utility (depends on settings from smsSuiteConfig)...
def generateCallFile(toExtension, tiffFilePath, callFileName):
	faxOptVariables = [	"FAXOPT(localstationid)=" + smsSuiteConfig.FAXID,
				"FAXOPT(ecm)=" + ("yes" if smsSuiteConfig.FAX_USE_ECM else "no"),
				"FAXOPT(minrate)=" + str(smsSuiteConfig.FAX_MIN_RATE),
				"FAXOPT(maxrate)=" + str(smsSuiteConfig.FAX_MAX_RATE),
				"FAXOPT(headerinfo)=" + smsSuiteConfig.FAXHEADER	]

	callFileGenerator.generateCallFile(	callFileName,
						toExtension,
						smsSuiteConfig.CALLER_ID_FAX,
						"SendFax",
						tiffFilePath + ",F",
						faxOptVariables,
						smsSuiteConfig.MAX_RETRIES_FAX,
						smsSuiteConfig.RETRY_TIME_FAX,
						smsSuiteConfig.WAIT_TIME_FAX,
						smsSuiteConfig.ARCHIVE_CALL_FILE_FAX	)

	return

# Simple header generator
def generateHeader(fromNumber, dateTime, messageReference):
	header = smsSuiteConfig.FAX_HEADER_TEXT
	header += str(fromNumber)
	header += smsSuiteConfig.FAX_TIME_TEXT
	header += datetime.datetime.fromisoformat(dateTime).strftime("%Y/%m/%d %H:%M:%S")
	header += " ("
	header += str(messageReference)
	header += ")"
	header += "\n"
	header += (len(header) * '-')
	header += "\n"

	return header

# Very simple function for writing message to the text file
def writeMessage(messageFileName, message):
	txt = open(messageFileName, "w")
	txt.write(message)
	txt.close()

	return

# All processing utility...
def process(fromNumber, toNumber, toExtension, message, dateTime, messageReference):
	try:
		# Prepare temporary directory
		oldDir = os.getcwd()
		dir = tempfile.TemporaryDirectory()
		os.chdir(dir.name)

		# Generate file names (to which number + date and time)
		textFileName = generateDateTimeName(str(toNumber) + "-", ".txt")
		tiffFileName = generateDateTimeName(str(toNumber) + "-", ".tiff")
		callFileName = generateDateTimeName(str(toNumber) + "-", ".call")

		# Prepare message with header and write it out to the text file
		messageWithHeader = generateHeader(fromNumber, dateTime, messageReference) + message
		writeMessage(textFileName, messageWithHeader)

		# Convert text to the G3 TIFF file
		tiffTools.textFileToTIFF(	tiffFileName,
						textFileName,
						smsSuiteConfig.FAX_RESOLUTION,
						smsSuiteConfig.FAX_FONT,
						smsSuiteConfig.FAX_TOP_MARGIN	)

		# Crop unnecessary white part (makes less fax recording paper waste)
		cutter.loadAndCrop(tiffFileName, cutter.calculateCutMargin(smsSuiteConfig.FAX_RESOLUTION, smsSuiteConfig.FAX_CUTTER_VALUE))

		# Move prepared fax page (G3 TIFF) to outgoing faxes directory
		subprocess.run(["mv", tiffFileName, smsSuiteConfig.FAX_IMG_DIR])

		# Generate call file
		generateCallFile(toExtension, smsSuiteConfig.FAX_IMG_DIR + "/" + tiffFileName, callFileName)

		# Move call file to the Asterisk's temporary spool folder (which should definitely be on the same disk 'outgoing' directory is)
		subprocess.run(["mv", callFileName, smsSuiteConfig.AST_TEMP_SPOOL])

		# Move call file to the Asterisk's 'outgoing' directory
		subprocess.run(["mv", smsSuiteConfig.AST_TEMP_SPOOL + "/" + callFileName, smsSuiteConfig.ASTERISK_SPOOL])

	except Exception as e:
		logError(str(e))

	finally:
		os.chdir(oldDir)
		dir.cleanup()

	return


# Autorun section...
if __name__ == "__main__":
	exitCode = 0

	try:
		if len(sys.argv) == 7:
			process(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
			exitCode = 0
		else:
			logError(smsSuiteConfig.WRONG_USE)
			exitCode = 1

	except Exception as e:
		logError(str(e))
		exitCode = 1

	exit(exitCode)
