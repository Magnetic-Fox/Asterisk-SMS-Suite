#!/usr/bin/env python3

# SMS to voice processor
#
# by Magnetic-Fox, 19.04.2025 - 28.11.2025
#
# (C)2025 Bartłomiej "Magnetic-Fox" Węgrzyn

import datetime
import voiceTools
import callFileTools
import smsSuiteConfig
import suiteLogger


# Asterisk call file creation wrapper (depending on smsSuiteConfig)...
def generateCallFile(toExtension, voiceFilePathNoExt, callFileName):
	callFileTools.generateCallFile(	callFileName,
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

# Simple header generator
def generateHeader(fromNumber, dateTime, messageReference):
	header = smsSuiteConfig.HEADER_TEXT_VOICE

	if smsSuiteConfig.READ_NUMBER_AS_DIGITS:
		header += '"' + voiceTools.prepareNumber(fromNumber) + '"'
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
		# Add header to the message
		messageWithHeader = generateHeader(fromNumber, dateTime, messageReference) + " " + message

		# Generate file names for voice and call file (to number and date and time)
		voiceFileNameNoExt = callFileTools.generateDateTimeName(str(toNumber) + "-")
		callFileName = callFileTools.generateDateTimeName(str(toNumber) + "-", ".call")

		# Generate voice file as a 8000Hz WAVE file
		voiceTools.textTo8k(messageWithHeader, smsSuiteConfig.VOICE_FILE_DIR + "/" + voiceFileNameNoExt + ".wav")

		# Generate call file
		generateCallFile(toExtension, smsSuiteConfig.VOICE_FILE_DIR + "/" + voiceFileNameNoExt, smsSuiteConfig.AST_TEMP_SPOOL + "/" + callFileName)

		# Move call file to the outgoing directory
		callFileTools.moveCallFile(callFileName, smsSuiteConfig.AST_TEMP_SPOOL, smsSuiteConfig.ASTERISK_SPOOL)

	except Exception as e:
		# Log any errors
		suiteLogger.logError(str(e))

	return
