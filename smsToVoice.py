#!/usr/bin/env python3

# Simple SMS to Voice relay utilizing Google Text-to-speech library (GTTS) and FFmpeg
#
# by Magnetic-Fox, 19.04.2025 - 15.11.2025
#
# (C)2025 Bartłomiej "Magnetic-Fox" Węgrzyn

import subprocess
import tempfile
import sys
import os
import datetime
import gtts
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

# Asterisk call file creation utility (depending on smsSuiteConfig)...
def generateCallFile(toExtension, voiceFilePathNoExt, callFileName):
	callFile = open(callFileName, "w")
	callFile.write("Channel: " + toExtension + "\n")
	callFile.write("CallerID: " + smsSuiteConfig.CALLER_ID_VOICE + "\n")
	callFile.write("MaxRetries: " + str(smsSuiteConfig.MAX_RETRIES_VOICE) + "\n")
	callFile.write("RetryTime: " + str(smsSuiteConfig.RETRY_TIME_VOICE) + "\n")
	callFile.write("WaitTime: " + str(smsSuiteConfig.WAIT_TIME_VOICE) + "\n")

	callFile.write("Archive: ")

	if smsSuiteConfig.ARCHIVE_CALL_FILE_VOICE:
		callFile.write("yes")
	else:
		callFile.write("no")

	callFile.write("\n")

	callFile.write("Application: Playback" + "\n")
	callFile.write("Data: " + voiceFilePathNoExt + "\n")
	callFile.close()

	return

# Number generator
def prepareNumber(number):
	output = ""

	for digit in str(number):
		output += digit + " "

	return output[:-1]

# Simple header generator
def generateHeader(fromNumber, dateTime, messageReference):
	header = smsSuiteConfig.HEADER_TEXT_VOICE

	if smsSuiteConfig.READ_NUMBER_AS_DIGITS:
		header += '"' + prepareNumber(fromNumber) + '"'
	else:
		header += '"' + str(fromNumber) + '"'

	if smsSuiteConfig.GIVE_DATE_VOICE:
		header += smsSuiteConfig.TIME_TEXT_VOICE
		header += datetime.datetime.fromisoformat(dateTime).strftime("%d-%m-%Y " + smsSuiteConfig.TIME_AT_TEXT_VOICE + " %H:%M:%S")

	if smsSuiteConfig.GIVE_REFERENCE_NUMBER_VOICE:
		header += smsSuiteConfig.REFERENCE_TEXT
		header += '"' + str(messageReference) + '"'

	header += "."

	return header

# All processing utility...
def process(fromNumber, toNumber, toExtension, message, dateTime, messageReference):
	try:
		# Prepare temporary directory
		oldDir = os.getcwd()
		dir = tempfile.TemporaryDirectory()
		os.chdir(dir.name)

		# Add header to the message
		messageWithHeader = generateHeader(fromNumber, dateTime, messageReference) + " " + message

		# Generate file names for voice and call file (to number and date and time)
		voiceFileName = generateDateTimeName(str(toNumber) + "-", ".mp3")
		callFileName = generateDateTimeName(str(toNumber) + "-", ".call")

		# Generate voice file using Google Text-to-speech library (GTTS)
		tts = gtts.gTTS(text = messageWithHeader, lang = smsSuiteConfig.LANG_VOICE, slow = smsSuiteConfig.VOICE_SLOW)
		tts.save(voiceFileName)

		# Convert MP3 file to 8000Hz WAVE file using FFmpeg
		fN, fExt = os.path.splitext(voiceFileName)
		subprocess.check_output(["ffmpeg", "-i", voiceFileName, "-af", "adelay=1s:all=true", "-ar", "8000", fN + ".wav"])

		# Move voice file to its outgoing directory
		subprocess.check_output(["mv", fN + ".wav", smsSuiteConfig.VOICE_FILE_DIR])

		# Store path to the voice file without extension (this is needed by Asterisk)
		voiceFilePathNoExt = smsSuiteConfig.VOICE_FILE_DIR + "/" + fN

		# Generate call file
		generateCallFile(toExtension, voiceFilePathNoExt, callFileName)

		# Move call file to the Asterisk's temporary spool directory (which definitely should be on the same disk as 'outgoing' directory!)
		subprocess.check_output(["mv", callFileName, smsSuiteConfig.AST_TEMP_SPOOL])

		# Move call file to the 'outgoing' directory
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
