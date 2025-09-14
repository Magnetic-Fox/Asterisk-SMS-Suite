#!/usr/bin/env python3

# SMS Suite Main Configuration File
# (some kind of defaults - have to be changed before use!)
#
# by Magnetic-Fox, 20.04 - 14.09.2025
#
# (C)2025 Bartłomiej "Magnetic-Fox" Węgrzyn


# Fax settings
FAX_HEADER_TEXT = "SMS from "
FAX_TIME_TEXT = " sent "

FAX_IMG_DIR = "/var/spool/T.38/outgoing"
CALLER_ID_FAX = '"YourAsteriskFAXCallerID" <Number>'

FAXID = "YourAsteriskFAXID"
FAXHEADER = "YourAsteriskFAXHeader"

# Set fax resolution
# (0 - 96 dpi/STANDARD, 1 - 198 dpi/FINE, 2 - 391 dpi/SUPER FINE)
FAX_RESOLUTION = 1

WAIT_TIME_FAX = 40
RETRY_TIME_FAX = 600
MAX_RETRIES_FAX = 10
ARCHIVE_CALL_FILE_FAX = True



# Voice settings
LANG_VOICE = "en"

HEADER_TEXT_VOICE = "SMS from "
TIME_TEXT_VOICE = " sent "
TIME_AT_TEXT_VOICE = "at"
REFERENCE_TEXT = " having reference number "

GIVE_DATE_VOICE = False
GIVE_REFERENCE_NUMBER_VOICE = False

VOICE_FILE_DIR = "/var/spool/Voice/outgoing"
CALLER_ID_VOICE = '"YourAsteriskVoiceCallerID" <Number>'

WAIT_TIME_VOICE = 40
RETRY_TIME_VOICE = 600
MAX_RETRIES_VOICE = 10
ARCHIVE_CALL_FILE_VOICE = True



# Asterisk's main spool folder
ASTERISK_SPOOL = "/var/spool/asterisk/outgoing"

# Asterisk's received SMS-es spool folder
AST_SMS_SPOOL = "/var/spool/asterisk/sms/morx"



# Miscellaneous
WRONG_USE = "Wrong use."
WRONG_NUMBER = "Wrong number."
WRONG_COMMAND = "Unknown command."
