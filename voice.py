import speech_recognition as sr
import wave
from datetime import datetime
import whisper
from whisper import Whisper
import json
import time
import pyttsx3
import openai
import os
model:Whisper  = whisper.load_model("base")

# create a new recognizer instance
recognizer = sr.Recognizer()
#openai.organization = os.environ["OPENAI_ORGANIZATION"]
openai.api_key = os.environ["OPENAI_API_KEY"]
# for model in openai.Model.list()["data"]:
#     print(model["id"])
# exit()

# create a TTS engine object
engine = pyttsx3.init()

# set the TTS voice
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id) # set to female voice

# use the default microphone as the audio source
while True:
    with sr.Microphone() as source:
        print("Say something!")
        # listen for audio and adjust for ambient noise
        recognizer.adjust_for_ambient_noise(source)
        # record audio until silence is detected
        audio = recognizer.listen(source)

        # write audio to a WAV file
        name_promt = str(time.mktime(datetime.now().timetuple()))[:-2] 
        print(name_promt)
        name_file_wave = name_promt + ".wav"
        with wave.open(name_file_wave, "wb") as wav_file:
            wav_file.setnchannels(1)  # mono
            wav_file.setsampwidth(2)  # 2 bytes per sample
            wav_file.setframerate(44100)  # 16 kHz sampling rate
            wav_file.writeframes(audio.get_wav_data())


        transcript = model.transcribe(name_file_wave)
        # transcript = model.transcribe(audio.get_wav_data())

        name_file_transcript = name_promt + ".json"
        with open(name_file_transcript, "w") as file:
            json.dump(transcript, file)
        print(transcript["text"])

        # set the prompt
        prompt = transcript["text"]

        # set the parameters for the API request
        messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
                ]

        response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messages)

        name_file_response = name_promt + "_repsonse.json"
        with open(name_file_response, "w") as file:
            json.dump(response, file)
            
        # check if the API request was successful
        print(response)
        if 1 < len (response['choices'][0]):
            # retrieve the response text from the API response
            print(response)
            response_text = response['choices'][0]['message']["content"]
            print(response_text)
            # speak the text
            engine.say(response_text)
            engine.runAndWait()
        else:
            # print the error message if the API request failed
            print(f'Error: {response["error"]["message"]}')

            

    
