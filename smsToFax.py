#!/usr/bin/env python3

# SMS to fax processor
#
# by Magnetic-Fox, 19.04.2025 - 28.11.2025
#
# (C)2025 Bartłomiej "Magnetic-Fox" Węgrzyn

import datetime
import cutter
import tiffTools
import callFileTools
import smsSuiteConfig
import suiteLogger


# Asterisk call file creation utility (depends on settings from smsSuiteConfig)...
def generateCallFile(toExtension, tiffFilePath, callFileName):
	# Prepare additional variables
	faxOptVariables = [	"FAXOPT(localstationid)=" + smsSuiteConfig.FAXID,
				"FAXOPT(ecm)=" + ("yes" if smsSuiteConfig.FAX_USE_ECM else "no"),
				"FAXOPT(minrate)=" + str(smsSuiteConfig.FAX_MIN_RATE),
				"FAXOPT(maxrate)=" + str(smsSuiteConfig.FAX_MAX_RATE),
				"FAXOPT(headerinfo)=" + smsSuiteConfig.FAXHEADER	]

	# Generate call file
	callFileTools.generateCallFile(	callFileName,
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

# All processing utility...
def process(fromNumber, toNumber, toExtension, message, dateTime, messageReference):
	try:
		# Generate file names (to which number + date and time)
		tiffFileName = callFileTools.generateDateTimeName(str(toNumber) + "-", ".tiff")
		callFileName = callFileTools.generateDateTimeName(str(toNumber) + "-", ".call")

		# Convert prepared text (header + message) to the G3 TIFF file
		tiffTools.textToTIFF(	smsSuiteConfig.FAX_IMG_DIR + "/" + tiffFileName,
					generateHeader(fromNumber, dateTime, messageReference) + message,
					smsSuiteConfig.FAX_RESOLUTION,
					smsSuiteConfig.FAX_FONT,
					smsSuiteConfig.FAX_TOP_MARGIN	)

		# Crop unnecessary white part (makes less fax recording paper waste)
		cutter.loadAndCrop(	smsSuiteConfig.FAX_IMG_DIR + "/" + tiffFileName,
					cutter.calculateCutMargin(smsSuiteConfig.FAX_RESOLUTION, smsSuiteConfig.FAX_CUTTER_VALUE)	)

		# Generate call file
		generateCallFile(toExtension, smsSuiteConfig.FAX_IMG_DIR + "/" + tiffFileName, smsSuiteConfig.AST_TEMP_SPOOL + "/" + callFileName)

		# Move call file to the Asterisk's outgoing directory
		callFileTools.moveCallFile(callFileName, smsSuiteConfig.AST_TEMP_SPOOL, smsSuiteConfig.ASTERISK_SPOOL)

	except Exception as e:
		# Log any errors
		suiteLogger.logError(str(e))

	return
