#!/usr/bin/env python3

# SMS Processor
#
# by Magnetic-Fox, 17.04.2025 - 27.11.2025
#
# (C)2025 Bartłomiej "Magnetic-Fox" Węgrzyn

# Based on previous Bash version, which was based
# on a solution found on wiki.faked.org/Asterisk/SMS

import os
import smsSuiteConfig
import getChanInfo
import smsToFax
import smsToVoice
import smsCommand
import smsTools
import amiSendSIPIM
import suiteLogger


# Messages processing function
def processMessages(messagesDirectory = smsSuiteConfig.AST_SMS_SPOOL):
	for messageFile in os.listdir(messagesDirectory):
		if os.path.isfile(messagesDirectory + "/" + messageFile):
			try:
				# Get message file and recipient information
				source, destination, message, dateTime, reference = smsTools.getMessageContents(messagesDirectory + "/" + messageFile)
				extension, service = getChanInfo.tryToGetChanInfo(destination)

				# If recipient want SMS-es
				if service == "S":
					smsTools.sendProperSMS(smsSuiteConfig.SMS_CENTRE_SEND_NR, extension, source, message, dateTime, reference, destination, smsSuiteConfig.USE_CONCATENATED_SMS)

				# If recipient want faxes
				elif service == "F":
					smsToFax.process(source, destination, extension, message, dateTime, reference)

				# If recipient want voice messages
				elif service == "V":
					smsToVoice.process(source, destination, extension, message, dateTime, reference)

				# Command processing
				elif service == "C":
					# Try to execute command
					try:
						commandResponse = smsCommand.process(source, destination, message)

					except:
						commandResponse = smsSuiteConfig.COMMAND_ERROR
						suiteLogger.logWarning(commandResponse)

					# Get sender information (to send response)
					sourceExtension, sourceService = getChanInfo.tryToGetChanInfo(source)

					# If recipient want SMS-es
					if sourceService == "S":
						smsTools.sendProperSMS(smsSuiteConfig.SMS_CENTRE_SEND_NR, sourceExtension, destination, commandResponse, None, None, source, smsSuiteConfig.USE_CONCATENATED_SMS)

					# If recipient want SIP messages
					elif sourceService == "T":
						if amiSendSIPIM.sendMessage(destination, source, commandResponse) != 0:
							suiteLogger.logWarning(smsSuiteConfig.CANNOT_SEND + " " + str(source) + ".")

					# Otherwise
					else:
						suiteLogger.logWarning(smsSuiteConfig.CANNOT_SEND + " " + str(source) + ".")

				# If recipient want SIP messages
				elif service == "T":
					if amiSendSIPIM.sendMessage(source, destination, message) != 0:
						# Get sender information (to send error)
						sourceExtension, sourceService = getChanInfo.tryToGetChanInfo(source)

						# Prepare error message
						errorMessage = smsSuiteConfig.CANNOT_DELIVER + " " + str(destination) + ". " +smsSuiteConfig.CANNOT_DELIVER_R1

						# If recipient want SMS-es
						if sourceService == "S":
							smsTools.sendProperSMS(smsSuiteConfig.SMS_CENTRE_SEND_NR, sourceExtension, smsSuiteConfig.SMS_CENTRE_RECV_NR, errorMessage, None, None, source, smsSuiteConfig.USE_CONCATENATED_SMS)

						# Otherwise
						else:
							suiteLogger.logWarning(smsSuiteConfig.CANNOT_SEND + " " + str(source) + ".")

				# Otherwise
				else:
					# Get sender information (to send error)
					sourceExtension, sourceService = getChanInfo.tryToGetChanInfo(source)

					# If recipient want SMS-es
					if sourceService == "S":
						# If user has deactivated messaging service
						if service == "N":
							errorMessage = smsSuiteConfig.CANNOT_DELIVER + " " + str(destination) + ". " + smsSuiteConfig.CANNOT_DELIVER_R2

						# Got unknown phone number
						else:
							errorMessage = smsSuiteConfig.CANNOT_DELIVER + " " + str(destination) + ". " + smsSuiteConfig.CANNOT_DELIVER_R3

						# Send error message
						smsTools.sendProperSMS(smsSuiteConfig.SMS_CENTRE_SEND_NR, sourceExtension, smsSuiteConfig.SMS_CENTRE_RECV_NR, errorMessage, None, None, source, smsSuiteConfig.USE_CONCATENATED_SMS)

					# Otherwise
					else:
						suiteLogger.logWarning(smsSuiteConfig.CANNOT_SEND + " " + str(source) + ".")

				# Remove message file (if it's safe to do so)
				if (messagesDirectory.strip() != "") and (messageFile.strip() != "") and (messagesDirectory.strip() + "/" + messageFile.strip() != "/"):
					os.remove(messagesDirectory + "/" + messageFile)

				else:
					# Cannot safely delete task
					suiteLogger.logWarning(smsSuiteConfig.CANNOT_DELETE_TASK)

			except:
				# Invalid file (non-SMS) found, skipped
				suiteLogger.logWarning(messageFile + smsSuiteConfig.REJECTED_FILE + " " + smsSuiteConfig.REJECTED_FILE_R1)

		else:
			# Probably not-a-file detected, skipped
			suiteLogger.logWarning(messageFile + smsSuiteConfig.REJECTED_FILE + " " + smsSuiteConfig.REJECTED_FILE_R2)


# Autorun section
if __name__ == "__main__":
	processMessages()
