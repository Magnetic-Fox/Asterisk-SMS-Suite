#!/usr/bin/env python3

# Simple SMS to Fax relay
#
# by Magnetic-Fox, 19.04.2025 - 13.09.2025
#
# (C)2025 Bartłomiej "Magnetic-Fox" Węgrzyn

import subprocess
import tempfile
import sys
import os
import datetime
import cutter
import smsSuiteConfig

# Simple error logging utility...
def logError(errorString):
        subprocess.check_output(["logger", errorString])
        return

# Asterisk call file creation utility...
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

# All processing utility...
def process(fromNumber, toNumber, toExtension, message, dateTime, messageReference):
	try:
		oldDir = os.getcwd()
		dir = tempfile.TemporaryDirectory()
		os.chdir(dir.name)

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

		all = header + message

		txt = open("message.txt", "w")
		txt.write(all)
		txt.close()

		currentTime = datetime.datetime.now()

		dateTimeName = str(toNumber)
		dateTimeName += "-"
		dateTimeName += str(currentTime.year)
		dateTimeName += "-"
		dateTimeName += str(currentTime.month)
		dateTimeName += "-"
		dateTimeName += str(currentTime.day)
		dateTimeName += "-"
		dateTimeName += str(currentTime.hour)
		dateTimeName += "-"
		dateTimeName += str(currentTime.minute)
		dateTimeName += "-"
		dateTimeName += str(currentTime.second)
		dateTimeName += "-"
		dateTimeName += str(currentTime.microsecond)

		tiffFileName = "fax-"
		tiffFileName += dateTimeName
		tiffFileName += ".tiff"

		callFileName = dateTimeName + ".call"

		paps = subprocess.Popen(["paps", "--top-margin=18", "--font=Monospace 10", "message.txt"], stdout = subprocess.PIPE)
		subprocess.check_output(["gs", "-sDEVICE=tiffg3", "-sOutputFile=" + tiffFileName, "-dBATCH", "-dNOPAUSE", "-dSAFER", "-dQUIET", "-"], stdin = paps.stdout)
		paps.wait()

		cutter.loadAndCrop(tiffFileName)

		# Resize for standard resolution (make it smaller)
		if smsSuiteConfig.FAX_RESOLUTION == 0:
			subprocess.check_output(["convert", tiffFileName, "-resize", "x50%", tiffFileName])

                # Resize for super fine resolution (make it bigger)
		elif smsSuiteConfig.FAX_RESOLUTION == 2:
			subprocess.check_output(["convert", tiffFileName, "-resize", "x200%", tiffFileName])

		subprocess.check_output(["tiffset", "-s", "296", "2", tiffFileName])
		subprocess.check_output(["tiffset", "-s", "282", "204.0", tiffFileName])

		# Standard resolution
		if smsSuiteConfig.FAX_RESOLUTION == 0:
			subprocess.check_output(["tiffset", "-s", "283", "98.0", tiffFileName])

		# Super fine resolution
		elif smsSuiteConfig.FAX_RESOLUTION == 2:
			subprocess.check_output(["tiffset", "-s", "283", "391.0", tiffFileName])

		# Fine resolution
		else:
			subprocess.check_output(["tiffset", "-s", "283", "196.0", tiffFileName])

		subprocess.check_output(["mv", tiffFileName, smsSuiteConfig.FAX_IMG_DIR])

		generateCallFile(toExtension, smsSuiteConfig.FAX_IMG_DIR + "/" + tiffFileName, callFileName)
		subprocess.check_output(["mv", callFileName, smsSuiteConfig.ASTERISK_SPOOL])

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
