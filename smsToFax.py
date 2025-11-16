#!/usr/bin/env python3

# Simple SMS to Fax relay
#
# by Magnetic-Fox, 19.04.2025 - 16.11.2025
#
# (C)2025 Bartłomiej "Magnetic-Fox" Węgrzyn

import subprocess
import tempfile
import sys
import os
import datetime
import cutter
import smsSuiteConfig

# Simple name generation helper
def generateDateTimeName(prefix = "", postfix = "", date = None):
	if date == None:
		date = datetime.datetime.now()
	return prefix + date.strftime("%Y-%m-%d-%H-%M-%S-%f") + postfix

# Simple error logging utility...
def logError(errorString):
        subprocess.check_output(["logger", errorString])
        return

# Asterisk call file creation utility (depends on settings from smsSuiteConfig)...
def generateCallFile(toExtension, tiffFilePath, callFileName):
	callFile = open(callFileName, "w")
	callFile.write("Channel: " + toExtension + "\n")
	callFile.write("CallerID: " + smsSuiteConfig.CALLER_ID_FAX + "\n")
	callFile.write("MaxRetries: " + str(smsSuiteConfig.MAX_RETRIES_FAX) + "\n")
	callFile.write("RetryTime: " + str(smsSuiteConfig.RETRY_TIME_FAX) + "\n")
	callFile.write("WaitTime: " + str(smsSuiteConfig.WAIT_TIME_FAX) + "\n")

	callFile.write("Archive: ")

	if smsSuiteConfig.ARCHIVE_CALL_FILE_FAX:
		callFile.write("yes")
	else:
		callFile.write("no")

	callFile.write("\n")

	callFile.write("Application: SendFax" + "\n")
	callFile.write("Data: " + tiffFilePath + ",F\n")
	callFile.write("SetVar: FAXOPT(localstationid)=" + smsSuiteConfig.FAXID + "\n")
	callFile.write("SetVar: FAXOPT(ecm)=yes" + "\n")
	callFile.write("SetVar: FAXOPT(minrate)=2400" + "\n")
	callFile.write("SetVar: FAXOPT(maxrate)=14400" + "\n")
	callFile.write("SetVar: FAXOPT(headerinfo)=" + smsSuiteConfig.FAXHEADER + "\n")
	callFile.close()

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

# Very simple for writing message to the text file
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

		# Prepare commands
		papsCommand = ["paps", "--top-margin=" + str(smsSuiteConfig.FAX_TOP_MARGIN), "--font=" + smsSuiteConfig.FAX_FONT, textFileName]
		ghscCommand = ["gs", "-sDEVICE=tiffg3", "-sOutputFile=" + tiffFileName, "-dBATCH", "-dNOPAUSE", "-dSAFER", "-dQUIET", "-"]

		# Convert text to the image and convert to the G3 TIFF file
		paps = subprocess.Popen(papsCommand, stdout = subprocess.PIPE)
		subprocess.check_output(ghscCommand, stdin = paps.stdout)
		paps.wait()

		# Crop unnecessary white part (makes less fax recording paper waste)
		cutter.loadAndCrop(tiffFileName)

		# Resize for standard resolution (make it smaller)
		if smsSuiteConfig.FAX_RESOLUTION == 0:
			subprocess.check_output(["convert", tiffFileName, "-resize", "x50%", tiffFileName])

                # Resize for super fine resolution (make it bigger)
		elif smsSuiteConfig.FAX_RESOLUTION == 2:
			subprocess.check_output(["convert", tiffFileName, "-resize", "x200%", tiffFileName])

		# Add parameters to the TIFF image (add resolution information)
		subprocess.check_output(["tiffset", "-s", "296", "2", tiffFileName])
		subprocess.check_output(["tiffset", "-s", "282", "204.0", tiffFileName])

		# Standard resolution
		if smsSuiteConfig.FAX_RESOLUTION == 0:
			subprocess.check_output(["tiffset", "-s", "283", "98.0", tiffFileName])

		# Super fine resolution (please note that not every fax will support it!)
		elif smsSuiteConfig.FAX_RESOLUTION == 2:
			subprocess.check_output(["tiffset", "-s", "283", "391.0", tiffFileName])

		# Fine resolution
		else:
			subprocess.check_output(["tiffset", "-s", "283", "196.0", tiffFileName])

		# Move prepared fax page (G3 TIFF) to outgoing faxes directory
		subprocess.check_output(["mv", tiffFileName, smsSuiteConfig.FAX_IMG_DIR])

		# Generate call file
		generateCallFile(toExtension, smsSuiteConfig.FAX_IMG_DIR + "/" + tiffFileName, callFileName)

		# Move call file to the Asterisk's temporary spool folder (which should definitely be on the same disk 'outgoing' directory is)
		subprocess.check_output(["mv", callFileName, smsSuiteConfig.AST_TEMP_SPOOL])

		# Move call file to the Asterisk's 'outgoing' directory
		subprocess.check_output(["mv", smsSuiteConfig.AST_TEMP_SPOOL + "/" + callFileName, smsSuiteConfig.ASTERISK_SPOOL])

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
