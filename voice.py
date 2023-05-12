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
import sys

if __name__ == "__main__":
    # read first argument are voice type
    if 1 < len(sys.argv):
        voice_type = sys.argv[1]
        if voice_type not in ["male", "female"]:
            raise Exception("Please provide voice type as `male` or `female`")
    else:
        raise Exception("Please provide voice type as `male` or `female`")
    

    if 2 < len(sys.argv):
        role = " ".join(sys.argv[2:])
    else:
        raise Exception("Please provide a role like `helpfull assitent` or `rowdy debater fellow in a bar`")
    print(role)

    model:Whisper  = whisper.load_model("base")

    # create a new recognizer instance
    recognizer = sr.Recognizer()
    openai.api_key = os.environ["OPENAI_API_KEY"]


    # create a TTS engine object
    engine = pyttsx3.init()

    # set the TTS voice
    voices = engine.getProperty('voices')
    if voice_type == "male":
        engine.setProperty('voice', voices[0].id) # set to male voice
    else:
        engine.setProperty('voice', voices[1].id) # set to female voice

    # use the default microphone as the audio source
    print(f"role: {role}")
    print(f"voice_type: {voice_type}")
    while True:
        with sr.Microphone() as source:
            print("Listening!")
            # listen for audio and adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source)
            # record audio until silence is detected'
            recognizer.pause_threshold = 1.0
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

            name_file_transcript = name_promt + ".json"
            with open(name_file_transcript, "w") as file:
                json.dump(transcript, file)
            print(transcript["text"])

            # set the prompt
            prompt = transcript["text"]

            # set the parameters for the API request
            messages = [
                    {"role": "system", "content": f"You are a {role}."},
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

                

        
