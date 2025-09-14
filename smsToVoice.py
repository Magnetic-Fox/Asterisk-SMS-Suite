#!/usr/bin/env python3

# Simple SMS to Voice relay utilizing Google Text-to-speech library (GTTS)
#
# by Magnetic-Fox, 19.04 - 13.09.2025
#
# (C)2025 Bartłomiej "Magnetic-Fox" Węgrzyn

import subprocess
import tempfile
import sys
import os
import datetime
import gtts
import smsSuiteConfig

# Simple error logging utility...
def logError(errorString):
	subprocess.check_output(["logger", errorString])
	return

# Asterisk call file creation utility...
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

# All processing utility...
def process(fromNumber, toNumber, toExtension, message, dateTime, messageReference):
	try:
		oldDir = os.getcwd()
		dir = tempfile.TemporaryDirectory()
		os.chdir(dir.name)

		header = smsSuiteConfig.HEADER_TEXT_VOICE
		header += '"' + str(fromNumber) + '"'

		if smsSuiteConfig.GIVE_DATE_VOICE:
			header += smsSuiteConfig.TIME_TEXT_VOICE
			header += datetime.datetime.fromisoformat(dateTime).strftime("%d-%m-%Y " + smsSuiteConfig.TIME_AT_TEXT_VOICE + " %H:%M:%S")

		if smsSuiteConfig.GIVE_REFERENCE_NUMBER_VOICE:
			header += smsSuiteConfig.REFERENCE_TEXT
			header += '"' + str(messageReference) + '"'

		header += "."

		all = header + " " + message

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

		voiceFileName = "voice-"
		voiceFileName += dateTimeName
		voiceFileName += ".mp3"

		tts = gtts.gTTS(text = all, lang = smsSuiteConfig.LANG_VOICE, slow = False)
		tts.save(voiceFileName)

		fN, fExt = os.path.splitext(voiceFileName)
		subprocess.check_output(["ffmpeg", "-i", voiceFileName, "-af", "adelay=1s:all=true", "-ar", "8000", fN + ".wav"])
		subprocess.check_output(["mv", fN + ".wav", smsSuiteConfig.VOICE_FILE_DIR])
		voiceFilePathNoExt = smsSuiteConfig.VOICE_FILE_DIR + "/" + fN

		callFileName = dateTimeName + ".call"
		generateCallFile(toExtension, voiceFilePathNoExt, callFileName)
		subprocess.check_output(["mv", callFileName, smsSuiteConfig.ASTERISK_SPOOL + "/" + callFileName])

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
