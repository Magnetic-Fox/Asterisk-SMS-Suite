#!/usr/bin/env python3

# SMS to voice processor
# utilizing Google Text-to-speech library (GTTS) and FFmpeg
#
# by Magnetic-Fox, 19.04.2025 - 26.11.2025
#
# (C)2025 Bartłomiej "Magnetic-Fox" Węgrzyn

import subprocess
import tempfile
import os
import datetime
import voiceTools
import callFileGenerator
import smsSuiteConfig
import suiteLogger


# Simple name generation helper
def generateDateTimeName(prefix = "", postfix = "", date = None):
	if date == None:
		date = datetime.datetime.now()
	return prefix + date.strftime("%Y-%m-%d-%H-%M-%S-%f") + postfix

# Asterisk call file creation utility (depending on smsSuiteConfig)...
def generateCallFile(toExtension, voiceFilePathNoExt, callFileName):
	callFileGenerator.generateCallFile(	callFileName,
						toExtension,
						smsSuiteConfig.CALLER_ID_VOICE,
						"Playback",
						voiceFilePathNoExt,
						None,
						smsSuiteConfig.MAX_RETRIES_VOICE,
						smsSuiteConfig.RETRY_TIME_VOICE,
						smsSuiteConfig.WAIT_TIME_VOICE,
						smsSuiteConfig.ARCHIVE_CALL_FILE_VOICE	)

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

		# Generate voice file and convert it to 8000Hz WAVE file
		voiceTools.textToMP3(voiceFileName, messageWithHeader, smsSuiteConfig.LANG_VOICE, smsSuiteConfig.VOICE_SLOW)
		fileName = voiceTools.MP3toWAV8(voiceFileName, smsSuiteConfig.VOICE_ADD_DELAY)

		# Move voice file to its outgoing directory
		subprocess.run(["mv", fileName + ".wav", smsSuiteConfig.VOICE_FILE_DIR])

		# Store path to the voice file without extension (this is needed by Asterisk)
		voiceFilePathNoExt = smsSuiteConfig.VOICE_FILE_DIR + "/" + fileName

		# Generate call file
		generateCallFile(toExtension, voiceFilePathNoExt, callFileName)

		# Move call file to the Asterisk's temporary spool directory (which definitely should be on the same disk as 'outgoing' directory!)
		subprocess.run(["mv", callFileName, smsSuiteConfig.AST_TEMP_SPOOL])

		# Move call file to the 'outgoing' directory
		subprocess.run(["mv", smsSuiteConfig.AST_TEMP_SPOOL + "/" + callFileName, smsSuiteConfig.ASTERISK_SPOOL])

	except Exception as e:
		suiteLogger.logError(str(e))

	finally:
		os.chdir(oldDir)
		dir.cleanup()

	return
