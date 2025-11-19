#!/usr/bin/env python3

# Voice tools for Asterisk utlizing gTTS and FFmpeg
#
# by Magnetic-Fox, 19.04.2025 - 19.11.2025
#
# (C)2025 Bartłomiej "Magnetic-Fox" Węgrzyn

import os
import gtts
import subprocess


# Text to MP3 converter (using gTTS)
def textToMP3(voiceFileName, inputText, language = "pl", speakSlowly = False):
	gtts.gTTS(text = inputText, lang = language, slow = speakSlowly).save(voiceFileName)
	return

# MP3 to 8000Hz wave converter (using FFmpeg; returning filename without extension)
def MP3toWAV8(voiceFileName, delay = True):
	fileName, fileExt = os.path.splitext(voiceFileName)
	ffmpegCommand = ["ffmpeg", "-i", voiceFileName]

	if delay:
		ffmpegCommand += ["-af", "adelay=1s:all=true"]

	ffmpegCommand += ["-ar", "8000", fileName + ".wav"]
	subprocess.run(ffmpegCommand)
	return fileName
