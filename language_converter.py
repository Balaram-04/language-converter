import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
import os
from playsound import playsound
import cv2
import mediapipe as mp
import time

# ---------------- SPEECH SETUP ----------------
recognizer = sr.Recognizer()
translator = Translator()

language_codes = {
    "english": "en",
    "hindi": "hi",
    "tamil": "ta",
    "telugu": "te",
    "kannada": "kn",
    "malayalam": "ml",
    "bengali": "bn",
    "marathi": "mr"
}

languages = list(language_codes.keys())
lang_index = 0
target_lang = languages[lang_index]
target_code = language_codes[target_lang]

# ---------------- MEDIAPIPE SETUP ----------------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

# ---------------- GESTURE DETECTION ----------------
def detect_gesture(hand_landmarks):
    thumb_tip = hand_landmarks.landmark[4]
    index_tip = hand_landmarks.landmark[8]
    middle_tip = hand_landmarks.landmark[12]

    # Simple logic (very basic but works for demo)
    if thumb_tip.y < index_tip.y and thumb_tip.y < middle_tip.y:
        return "THUMBS_UP"
    elif index_tip.y < middle_tip.y:
        return "PEACE"
    else:
        return "FIST"

# ---------------- SPEECH FUNCTION ----------------
def speech_to_speech():
    with sr.Microphone() as source:
        print("\n🎤 Speak now...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

        text = recognizer.recognize_google(audio)
        print("You said:", text)

        translated = translator.translate(text, dest=target_code)
        translated_text = translated.text

        print("🌍 Translated:", translated_text)

        tts = gTTS(text=translated_text, lang=target_code)
        filename = "output.mp3"
        tts.save(filename)

        playsound(filename)
        os.remove(filename)

# ---------------- MAIN LOOP ----------------
running = False
last_action_time = 0

print("Show gestures to control system...")

while True:
    success, frame = cap.read()
    frame = cv2.flip(frame, 1)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        for handLms in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)

            gesture = detect_gesture(handLms)

            # prevent repeated triggers
            if time.time() - last_action_time > 2:

                # 👍 START
                if gesture == "THUMBS_UP":
                    print("👍 START listening")
                    running = True
                    last_action_time = time.time()

                # ✊ STOP
                elif gesture == "FIST":
                    print("✊ STOP system")
                    running = False
                    last_action_time = time.time()

                # ✌️ CHANGE LANGUAGE
                elif gesture == "PEACE":
                    lang_index = (lang_index + 1) % len(languages)
                    target_lang = languages[lang_index]
                    target_code = language_codes[target_lang]
                    print("🌐 Language changed to:", target_lang)
                    last_action_time = time.time()

    cv2.putText(frame, f"Lang: {target_lang}", (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Gesture Control System", frame)

    # If running, do speech translation
    if running:
        try:
            speech_to_speech()
        except Exception as e:
            print("Error:", e)
            running = False

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
