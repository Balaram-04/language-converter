import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
import os

recognizer = sr.Recognizer()

with sr.Microphone() as source:
    print("Say something:")
    audio = recognizer.listen(source)

try:

    text = recognizer.recognize_google(audio)
    print(f"You said: {text}")
    
    translator = Translator()
    translated = translator.translate(text, src='en', dest='ml')
    print(f"Translated text: {translated.text}")
    tts = gTTS(text=translated.text, lang='ml')
    tts.save("translated_audio.mp3")

    os.system("start translated_audio.mp3")  

except sr.UnknownValueError:
    print("Sorry, I could not understand the audio.")
except sr.RequestError:
    print("Could not request results; check your network connection.")
