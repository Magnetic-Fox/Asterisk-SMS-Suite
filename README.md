# Asterisk SMS Suite

## Introduction

The goal of this project is to provide a set of tools for processing and controlling the flow of short messages of different types in the Asterisk PBX.
This suite can correctly route SMS-es and SIP instant messages and also resend them as a fax or voice messages to the non-messaging channels making it a ready-to-use solution for instant messaging of any kind.

## Important notes

This set of tools was created for SIP-configured Asterisk working on Linux system (especially Debian).
It should work with PJSIP configurations, but I haven't tested it (it's yet to be done in my configuration).
These tools might need some kind of fine tuning to work with PJSIP configurations properly.

Default configuration values (provided in the `smsSuiteConfig.py` file) assume that Asterisk and its directories are located in their default locations (`/etc/asterisk`, `/var/spool/asterisk`, etc.) and that there is a dedicated directory for all scripts at `/etc/asterisk/scripts`.

**This solution was created for Asterisk 16.28.** However it should work with the newer versions.
I haven't tested if these tools can work properly on systems other than Linux.

## Differences between SMS technology and SIP messaging

As far as I have seen, people often confuse SMS technology with SIP instant messaging. **They are completely different protocols!**
SMS requires some kind of an explicit central point (also called SMS Centre/SMS Centrum) which acts like a server which receive, store, process and resend messages (and, ideally, should keep them for some time if the receiving end is offline).
SIP messaging is much more automated and then looks more like a point-to-point service as it doesn't explicitly use such a thing like SMS Centre (**but Asterisk still has to do processing internally**). However, this technology is definitely less powerful than classic SMS service.

And, the most important thing - SMS Centre actually **can** work even on the classic landline telephony (POTS) using FSK modulation (which is, in my opinion, such a great thing that it really works in Asterisk!) allowing You to use an old analogue phone with SMS support with it.
In contrast, **SIP messages can't** as they are protocol based. I know no VoIP ATA that could turn this into the FSK SMS or something similar. There are probably IP phones supporting SIP messaging, but I don't know of any. The only ones I know and have used are software SIP clients like MicroSIP or Zoiper (both really good).

## Database with chosen messaging services

As this solution was prepared to be able to resend messages as faxes or voice calls, it needs to know what kind of service the recipient has activated.
For this to work, it needs to have a simple table in a database with information about chosen service, phone number and Asterisk extension.
There are at least three columns needed:

* Account -> varchar(100) - phone number
* Message -> varchar(1) - character indicating chosen service
* Extension -> varchar(100) - Asterisk extension (e.g. SIP/1000)

`getChanInfo.py` is responsible for gathering this information and relay it to other scripts. It was prepared to utilize MySQL database (using MySQL connector). If You need to use other database system, You have to change it in this script.

## Service indicators

I've defined six indicators for services:

* S - normal SMS operation (SMS Centre)
* F - delivering messages as faxes
* V - delivering messages as a voice synthesis
* C - being simple command service (automated SMS reciver and answerer)
* T - SIP messaging operation
* N - no messaging at all (disable messaging delivery feature for the chosen number)

## Dependencies

These tools need some other packages and libraries to work.
Here is the list (hope I remember everything):

1. Asterisk (of course)
2. smsq (should be part of the Asterisk package)
3. pyst2 (Python Asterisk helper; for AGI and AMI)
4. Pillow (PIL)
5. gTTS (simple Python voice synthesis helper utilizing Google Translate)
6. MySQL Connector for Python (mysql.connector)
7. paps
8. ghostscript (gs)
9. Imagemagick (convert)
10. libtiff-tools (tiffset)
11. FFmpeg (ffmpeg)

## Default (and additional) directories

Default configurations provided here assume that Asterisk and other tools are in the specific locations.
Here is the list:

1. `/etc/asterisk` - main configuration directory for Asterisk
2. `/etc/asterisk/scripts` - **additional** directory for all scripts from this suite
3. `/var/spool/asterisk` - spool directory for Asterisk
4. `/var/spool/asterisk/sms` - SMS part of Asterisk's spool directory
5. `/var/spool/asterisk/sms/morx` - directory for received SMS-es
6. `/var/spool/asterisk/outgoing` - directory for `.call` files (originating calls)
7. `/var/spool/T.38` - **additional** directory for faxes (don't have to be T.38 - I've used such name, because T.38 was first way of faxing in Asterisk I used; now I'm using audio stream but the name stayed the same ;))
8. `/var/spool/T.38/outgoing` - **additional** directory for TIFFs to be sent
9. `/var/spool/Voice` - **additional** directory for voice files
10. `/var/spool/Voice/outgoing` - **additional** directory for voice files to be played on call

Additional above means that those directories didn't exist previously in the installation.
They were created by me to make performing additional functions easier.
They are now **used and necessary** in this software (`scripts` in the configurations, `T.38` and `Voice` in spool) unless You decide to place things another way (everything can be configured via `smsSuiteConfig.py` file).

## Tools, in brief

The main functionality is provided by `extensions.conf` file and `smsProcess.py` script.
Extensions file define all needed extensions and some basic operations (I've uploaded part of mine describing how to use my tools) and the Python script processes all SMS-es received by SMS Centre (also these received before which weren't processed and remains in the `morx` directory).
All other scripts are just tools used by the main script to get information about channel and chosen service, prepare other type of message (fax, voice synthesis, etc.) or to post SIP message, etc.

1. `extensions.conf` - configuration file for Asterisk, which still does main part of the job (it's called `extensions.conf.part` in this repository, because it's only a part here)
2. `smsProcess.py` - main SMS processor/router
3. `getChanInfo.py` - helper for gathering number information (chosen service, channel extension, etc.)
4. `smsToFax.py` - fax page and call creator
5. `smsToVoice.py` - voice synthesis and call creator
6. `smsCommand.py` - SMS commands processor (just an example to be extended to be something better)
7. `cutter.py` - cutting helper for making fax pages shorter (from [Mail2Fax](https://github.com/Magnetic-Fox/Mail2Fax) project)
8. `agiGetChanInfo.py` - AGI wrapper for `getChanInfo.py`
9. `agiPostSMS.py` - AGI tool for posting SMS-es like they were received by SMS Centre (for routing SIP messages to SMS)
10. `amiSendSIPIM.py` - AMI tool for sending SIP instant messages (for routing SMS-es to SIP messages)
11. `concatenatedSMSSender.py` - helper for sending concatenated SMS-es (for messages longer than 160 characters)
12. `callFileGenerator.py` - helper for creating call files
13. `tiffTools.py` - helper for text-to-TIFF conversion, resizing and applying resolution information to the TIFF files (also from [Mail2Fax](https://github.com/Magnetic-Fox/Mail2Fax) project)
14. `voiceTools.py` - helper for voice synthesis and converting audio files to 8000 Hz WAVE
15. `smsTools.py` - helper for sending SMS-es and gathering data from message files
16. `suiteLogger.py` - project-specific helper for easy warnings and errors logging
17. `smsSuiteConfig.py` - configuration file for all tools
18. `sqlConfig.py` - configuration file for SQL credentials
19. `amiConfig.py` - configuration file for AMI credentials

In fact, only `smsProcess.py`, `agiGetChanInfo.py` and `agiPostSMS.py` are explicitly seen as used (in `extensions.conf`).
Use of other tools is automated (seen in `smsProcess.py` or other scripts).

## Disclaimer

I've made much effort to provide here working code and solutions with hope they'll be useful and free from any bugs.
However I can't guarantee anything. The software and solutions here are provided "AS IS" and **I take no responsibility for anything. You're using them on Your own risk!**

## License

Free for personal use. You probably shouldn't use these solutions commercially (as they are not so good tested to be intended to).
However, if You still like to anyway, please ask me before.

Bartłomiej "Magnetic-Fox" Węgrzyn,
April 17, 2025 - November 26, 2025
