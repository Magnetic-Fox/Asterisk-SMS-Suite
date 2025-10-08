#!/bin/bash

# SMS processor utility
#
# by Magnetic-Fox, 17.04 - 13.09.2025, 08.10.2025
#
# (C)2025 Bartłomiej "Magnetic-Fox" Węgrzyn

# Based on solution found on wiki.faked.org/Asterisk/SMS



# SMS-related information (SMS Centrum's receiving and sending number and Asterisk spool directory for received SMS-es)
SPOOL='/var/spool/asterisk/sms/morx'
SMSCR='9000'
SMSCS='9001'

# Additional SMS settings (switch for concatenated SMS support)
USECONCAT=1

# Other software paths (should be absolute)
CHANINFO='/etc/asterisk/scripts/getChanInfo.py'
SMSTOFAX='/etc/asterisk/scripts/smsToFax.py'
SMSTOSND='/etc/asterisk/scripts/smsToVoice.py'
SMSCMDPY='/etc/asterisk/scripts/smsCommand.py'
SIPIMSND='/etc/asterisk/scripts/amiSendSIPIM.py'
SMSCONCT='/etc/asterisk/scripts/concatenatedSMSSender.py'

# Error texts presented to user (avoid non-ASCII characters!)
CANTDELIVER='Nie udalo sie dostarczyc wiadomosci SMS do numeru'

# Error texts logged on server (whatever You wish)
CANNOTSEND='Nie udało się wysłać wiadomości SMS do numeru'
CANTDELTASK='Nie udało się bezpiecznie usunąć odebranej wiadomości SMS!'



# Actual script goes here. Let's process all previously received messages
for SMS in `ls -1 "$SPOOL"`; do
	# Get all information from received message
	SRC=`grep -e '^oa=' "$SPOOL/$SMS" | sed 's/oa=//'`
	DST=`grep -e '^da=' "$SPOOL/$SMS" | sed 's/da=//'`
	MSG=`grep -e '^ud=' "$SPOOL/$SMS" | sed 's/ud=//'`
	SCTS=`grep -e '^scts=' "$SPOOL/$SMS" | sed 's/scts=//'`
	MR=`grep -e '^mr=' "$SPOOL/$SMS" | sed 's/mr=//'`

	# Get information about destination number for further processing
	CHAN_SERVICE=`${CHANINFO} "${DST}"`
	EXTENSION=`echo "$CHAN_SERVICE" | head -n 1 | tr -d '\n'`
	SERVICE=`echo "$CHAN_SERVICE" | tail -n 1 | tr -d '\n'`

	# Route message properly (according to the selected service)

	# Deliver SMS normally
	if [ "${SERVICE}" == "S" ]; then
		if [ $USECONCAT -eq 1 ] && [ ${#MSG} -gt 160 ]; then
			${SMSCONCT} "${SMSCS}" "${EXTENSION}" "${SRC}" "${MSG}" "${SCTS}" "${MR}" "${DST}"
		else
			smsq --mt --tx --mttx-callerid="${SMSCS}" --mttx-channel="${EXTENSION}" --oa="${SRC}" --ud="${MSG}" --scts="${SCTS}" --mr="${MR}" --queue="${DST}"
		fi

	# Deliver SMS as a fax
	elif [ "${SERVICE}" == "F" ]; then
		${SMSTOFAX} "${SRC}" "${DST}" "${EXTENSION}" "${MSG}" "${SCTS}" "${MR}"

	# Deliver SMS as a voice call
	elif [ "${SERVICE}" == "V" ]; then
		${SMSTOSND} "${SRC}" "${DST}" "${EXTENSION}" "${MSG}" "${SCTS}" "${MR}"

	# Got command SMS - process it and send back an answer
	elif [ "${SERVICE}" == "C" ]; then
		# First, try to execute specified command (remember to always make safe use of incomming message in the SMSCMDPY!)
		SMS_RESPONSE=`${SMSCMDPY} "${SRC}" "${DST}" "${MSG}"`

		# Then, get information about source number for further processing
		CHAN_SERVICE_SRC=`${CHANINFO} "${SRC}"`
		SRC_EXTENSION=`echo "$CHAN_SERVICE_SRC" | head -n 1 | tr -d '\n'`
		SRC_SERVICE=`echo "$CHAN_SERVICE_SRC" | tail -n 1 | tr -d '\n'`

		# If source number can receive SMS back, then send command's answer
		if [ "${SRC_SERVICE}" == "S" ]; then
			if [ $USECONCAT -eq 1 ] && [ ${#SMS_RESPONSE} -gt 160 ]; then
				${SMSCONCT} "${SMSCS}" "${SRC_EXTENSION}" "${DST}" "${SMS_RESPONSE}" "XPARAM_NONE" "XPARAM_NONE" "${SRC}"
			else
				smsq --mt --tx --mttx-callerid="${SMSCS}" --mttx-channel="${SRC_EXTENSION}" --oa="${DST}" --ud="${SMS_RESPONSE}" --queue="${SRC}"
			fi

		# If source number can receive SIP IM back, then send command's answer
		elif [ "${SRC_SERVICE}" == "T" ]; then
			${SIPIMSND} "${DST}" "${SRC}" "${SMS_RESPONSE}"

			# Log if there was an error
			if [ $? -ne 0 ]; then
				echo "${CANNOTSEND} ${SRC}." | logger
			fi

		# If not, then drop it, but leave some information in the server log
		else
			echo "${CANNOTSEND} ${SRC}." | logger
		fi

	# Deliver SMS as an SIP IM
	elif [ "${SERVICE}" == "T" ]; then
		${SIPIMSND} "${SRC}" "${DST}" "${MSG}"

		# If delivery failed
		if [ $? -ne 0 ]; then
			# Get information about source number for further processing
			CHAN_SERVICE_SRC=`${CHANINFO} "${SRC}"`
			SRC_EXTENSION=`echo "$CHAN_SERVICE_SRC" | head -n 1 | tr -d '\n'`
			SRC_SERVICE=`echo "$CHAN_SERVICE_SRC" | tail -n 1 | tr -d '\n'`

			# If source number can receive SMS back, then send it
			if [ "${SRC_SERVICE}" == "S" ]; then
				ERR_MESSAGE="${CANTDELIVER} ${DST}."

				if [ $USECONCAT -eq 1 ] && [ ${#ERR_MESSAGE} -gt 160 ]; then
					${SMSCONCT} "${SMSCS}" "${SRC_EXTENSION}" "${SMSCR}" "${ERR_MESSAGE}" "XPARAM_NONE" "XPARAM_NONE" "${SRC}"
				else
					smsq --mt --tx --mttx-callerid="${SMSCS}" --mttx-channel="${SRC_EXTENSION}" --oa="${SMSCR}" --ud="${ERR_MESSAGE}" --queue="${SRC}"
				fi

			# If not, then drop it, but leave some information in the server log
			else
				echo "${CANNOTSEND} ${SRC}." | logger
			fi
		fi

	# Got unknown destination number (deliver error message)
	else
		# Get information about source number for further processing
		CHAN_SERVICE_SRC=`${CHANINFO} "${SRC}"`
		SRC_EXTENSION=`echo "$CHAN_SERVICE_SRC" | head -n 1 | tr -d '\n'`
		SRC_SERVICE=`echo "$CHAN_SERVICE_SRC" | tail -n 1 | tr -d '\n'`

		# If source number can receive SMS back, then send it
		if [ "${SRC_SERVICE}" == "S" ]; then
			ERR_MESSAGE="${CANTDELIVER} ${DST}."

			if [ $USECONCAT -eq 1 ] && [ ${#ERR_MESSAGE} -gt 160 ]; then
				${SMSCONCT} "${SMSCS}" "${SRC_EXTENSION}" "${SMSCR}" "${ERR_MESSAGE}" "XPARAM_NONE" "XPARAM_NONE" "${SRC}"
			else
				smsq --mt --tx --mttx-callerid="${SMSCS}" --mttx-channel="${SRC_EXTENSION}" --oa="${SMSCR}" --ud="${ERR_MESSAGE}" --queue="${SRC}"
			fi

		# If not, then drop it, but leave some information in the server log
		else
			echo "${CANNOTSEND} ${SRC}." | logger
		fi
	fi

	# Try to safely remove SMS task (from the spool directory of received messages)
	if [ ! -z `echo "${SPOOL}" | tr -d '[:space:]'` ]; then
		if [ ! -z `echo "${SMS}" | tr -d '[:space:]'` ]; then
			rm "$SPOOL/$SMS"
		else
			# Cannot safely delete SMS task - log this in the server log
			echo "${CANTDELTASK}" | logger
		fi
	else
		# Cannot safely delete SMS task - log this in the server log
		echo "${CANTDELTASK}" | logger
	fi
done
