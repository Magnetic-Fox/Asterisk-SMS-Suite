#!/usr/bin/env python3

# SMS Suite Configuration File
# (some kind of defaults - have to be changed before use!)
#
# by Magnetic-Fox, 20.04.2025 - 26.11.2025
#
# (C)2025 Bartłomiej "Magnetic-Fox" Węgrzyn


# SMS centre settings
SMS_CENTRE_RECV_NR = 9000
SMS_CENTRE_SEND_NR = 9001
USE_CONCATENATED_SMS = True


# Logger settings
LOGGER_ADDRESS = "/dev/log"


# Error texts presented to user (avoid non-ASCII characters!)
CANNOT_DELIVER = "Cannot deliver SMS to"
CANNOT_DELIVER_R1 = "VoIP user not logged in."
CANNOT_DELIVER_R2 = "Subscriber has disabled messaging service."
CANNOT_DELIVER_R3 = "Number does not exist."
COMMAND_ERROR = "Unable to complete the order. Please try again in a few minutes."

# Error texts logged on server (whatever You wish)
CANNOT_SEND = "Cannot send SMS to"
CANNOT_DELETE_TASK = "Cannot safely remove received SMS!"
REJECTED_FILE = " rejected."
REJECTED_FILE_R1 = "Invalid message file."
REJECTED_FILE_R2 = "Not a file?"


# Asterisk's main spool directory
ASTERISK_SPOOL = "/var/spool/asterisk/outgoing"

# Asterisk's received SMS-es spool directory
AST_SMS_SPOOL = "/var/spool/asterisk/sms/morx"

# Asterisk's temporary spool directory
AST_TEMP_SPOOL = "/var/spool/asterisk/tmp"


# Fax settings
FAX_HEADER_TEXT = "Text message from "
FAX_TIME_TEXT = " sent "

FAX_IMG_DIR = "/var/spool/T.38/outgoing"
CALLER_ID_FAX = '"YourAsteriskFAXCallerID" <Number>'

FAXID = "YourAsteriskFAXID"
FAXHEADER = "YourAsteriskFAXHeader"

# Set fax resolution
# (0 - 98 dpi/STANDARD, 1 - 196 dpi/FINE, 2 - 391 dpi/SUPER FINE)
FAX_RESOLUTION = 1

FAX_TOP_MARGIN = 18
FAX_FONT = "Monospace 10"

FAX_CUTTER_VALUE = 94

FAX_USE_ECM = True
FAX_MIN_RATE = 2400
FAX_MAX_RATE = 14400

WAIT_TIME_FAX = 40
RETRY_TIME_FAX = 600
MAX_RETRIES_FAX = 10
ARCHIVE_CALL_FILE_FAX = True


# Voice settings
LANG_VOICE = "en"
VOICE_SLOW = False
VOICE_ADD_DELAY = True

HEADER_TEXT_VOICE = "Message from "
TIME_TEXT_VOICE = " sent "
TIME_AT_TEXT_VOICE = "at"
REFERENCE_TEXT = " having reference number "

GIVE_DATE_VOICE = False
GIVE_REFERENCE_NUMBER_VOICE = False

READ_NUMBER_AS_DIGITS = True

VOICE_FILE_DIR = "/var/spool/Voice/outgoing"
CALLER_ID_VOICE = '"YourAsteriskVoiceCallerID" <Number>'

WAIT_TIME_VOICE = 40
RETRY_TIME_VOICE = 600
MAX_RETRIES_VOICE = 10
ARCHIVE_CALL_FILE_VOICE = True


# Miscellaneous
WRONG_USE = "Wrong use."
WRONG_NUMBER = "Wrong number."
WRONG_COMMAND = "Unknown command."
