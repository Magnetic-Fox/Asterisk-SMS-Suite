#!/usr/bin/env python3

# Voice tools for Asterisk utlizing gTTS and FFmpeg
#
# by Magnetic-Fox, 19.04.2025 - 28.11.2025
#
# (C)2025 Bartłomiej "Magnetic-Fox" Węgrzyn

import os
import io
import gtts
import subprocess


# Text to MP3 file converter
def textToMP3(voiceFileName, inputText, language = "pl", speakSlowly = False):
	gtts.gTTS(text = inputText, lang = language, slow = speakSlowly).save(voiceFileName)
	return

# Text to MP3 data converter
def textToMP3Data(inputText, language = "pl", speakSlowly = False):
	tempData = io.BytesIO()
	gtts.gTTS(text = inputText, lang = language, slow = speakSlowly).write_to_fp(tempData)
	tempData.seek(0)
	return tempData.read()

# Input file to 8000Hz audio converter (also returning filename without extension)
def inputTo8k(voiceFileName, delay = True):
	fileName, fileExt = os.path.splitext(voiceFileName)
	ffmpegCommand = ["ffmpeg", "-i", voiceFileName]

	if delay:
		ffmpegCommand += ["-af", "adelay=1s:all=true"]

	ffmpegCommand += ["-ar", "8000", fileName + ".wav"]
	subprocess.run(ffmpegCommand)
	return fileName

# Input data to 8000Hz audio converter
def inputDataTo8k(inputData, voiceFileName, delay = True):
	ffmpegCommand = ["ffmpeg", "-i", "-"]

	if delay:
		ffmpegCommand += ["-af", "adelay=1s:all=true"]

	ffmpegCommand += ["-ar", "8000", voiceFileName]
	ffmpeg = subprocess.Popen(ffmpegCommand, stdin = subprocess.PIPE)
	ffmpeg.communicate(inputData)

	return

# Text to 8000Hz audio converter (wrapper)
def textTo8k(inputText, voiceFileName, language = "pl", speakSlowly = False, delay = True):
	inputDataTo8k(textToMP3Data(inputText, language, speakSlowly), voiceFileName, delay)
	return

# Number spell preparation function
def prepareNumber(number):
	output = ""

	for digit in str(number):
		output += digit + " "

	return output[:-1]

# Simple helper for returning time parts as a string proper way (4 -> 04, etc.)
def outputWithZero(input):
	if input < 10:
		return "0" + str(input)
	else:
		return str(input)
