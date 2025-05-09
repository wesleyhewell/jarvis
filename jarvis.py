import openai
import pyttsx3
import speech_recognition as sr
import pvporcupine
import pyaudio
import struct
import time
from dotenv import load_dotenv
import os

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
porcupine = pvporcupine.create(
    access_key = os.getenv("ACCESS_KEY"),
    keyword_paths=['./hey_jarvis.ppn']
)

# Start an audio stream for wake word detection
# pa = pyaudio.PyAudio()
# audio_stream = pa.open(
#     rate = porcupine.sample_rate,
#     channels = 1, 
#     format = pyaudio.paInt16,
#     input = True, 
#     frames_per_buffer = porcupine.frame_length
# )

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 160)

# Function to convert text to speech and play it
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to capture speech and convert it to text
def listen(): 
    r = sr.Recognizer()     # Create a recognizer instance
    with sr.Microphone() as source:       # Use default microphone as input
        print('Listening...')
        r.adjust_for_ambient_noise(source)      # Reduce background noise
        try: 
            audio = r.listen(source, timeout = 10)
            text = r.recognize_google(audio)
            print(f'You said: {text}')
            return text
        except sr.UnknownValueError:        # Handle case when speech is not understood
            print("Sorry, I don't understand.")
            return None
        except sr.RequestError:     # Handle case when service in unavailable
            print("Speech recognition is unavailable.")
            return None
        
# Function to send text to OpenAI and return AI response
def ask_open_ai(prompt): 
    response = openai.chat.completions.create(
        model = 'gpt-4o-mini',
        messages = [
            {"role": "developer", "content": "You are to act like JARVIS, Tony Stark's AI assistant from Iron Man, who has now been assigned to serve me, Wesley Hewell."},
            {"role": "developer", "content": "Please provide responses in a concise manner."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content      # Extract and return response from OpenAI

# Wake word detection loop 
def detect_wake_word(): 
    print("Waiting for wake word... ")

    # Reinitialize the audio stream
    pa = pyaudio.PyAudio()
    audio_stream = pa.open(
        rate = porcupine.sample_rate,
        channels = 1, 
        format = pyaudio.paInt16,
        input = True, 
        frames_per_buffer = porcupine.frame_length
    )

    try:
        while True: 
            pcm = audio_stream.read(porcupine.frame_length, exception_on_overflow = False)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

            keyword_index = porcupine.process(pcm)
            if keyword_index >= 0: 
                print("Wake word detected.")
                speak("Yes, sir.")
                return
    finally:
        audio_stream.stop_stream()
        audio_stream.close()
        pa.terminate

# Main function for JARVIS
def main():
    speak("Hello, I am JARVIS.")

    while True: 
        detect_wake_word()

        active_until = time.time() + 20     # Keep JARVIS active for 20 seconds without wake word

        while time.time() < active_until:
            user_input = listen()

            if user_input: 
                active_until = time.time() + 20

                if "goodbye" in user_input.lower():
                    speak("Goodbye, sir.")
                    break

                response = ask_open_ai(user_input)
                print("JARVIS: ", response)
                speak(response)
        
        print("Returning to wake mode... ")

if __name__ == "__main__":
    main()
