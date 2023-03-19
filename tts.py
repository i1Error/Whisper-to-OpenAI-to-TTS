import openai
import json
import time
import requests
from pydub import AudioSegment
from pydub.playback import play
import io
import pyttsx3

EL_key = "Eleven Labs Api key"
EL_voice = "VR6AewLTigWG4xSOukaG" #https://api.elevenlabs.io/v1/voices
OAI_key = "Open AI API key"

def init():
    global engine
    engine = pyttsx3.init()
    engine.setProperty('rate', 180)    # Speed of the speech
    engine.setProperty('volume', 1)  # Volume of the speech
    voice = engine.getProperty('voices') #get the available voices
    engine.setProperty('voice', voice[1].id) #changing voice to index 1 for female voice

def tts(message):

    url = f'https://api.elevenlabs.io/v1/text-to-speech/{EL_voice}'
    headers = {
        'accept': 'audio/mpeg',
        'xi-api-key': EL_key,
        'Content-Type': 'application/json'
    }
    data = {
        'text': message,
        'voice_settings': {
            'stability': 0.75,
            'similarity_boost': 0.75
        }
    }
    response = requests.post(url, headers=headers, json=data, stream=True)
    audio_content = AudioSegment.from_file(io.BytesIO(response.content), format="mp3")
    
    play(audio_content)

def llm(message):
    #language model
    openai.api_key = OAI_key
    response = openai.Completion.create(
      model="text-davinci-003",
      prompt=f"This is how a paranoid schizophrenic female streamer responded in a conversation. She would respond in a tense manner. \n\nShe would talk about the message and would elaborate on it as well as share some of her experiences if possible. She would also go on a tangent.\n#########\n{message}\n#########\n",
      #customizable prompt (system prompt)
      temperature=0.9,
      max_tokens=128,
      top_p=1,
      frequency_penalty=1,
      presence_penalty=1
    )

    json_object = json.loads(str(response))
    return(json_object['choices'][0]['text'])

if __name__ == "__main__":
    init()
    print("\n\nInitialized!\n\n")
    while True:
        message = input('Enter message:')
        if message == "stop programm tts":
            break
        print("\n\nReset!\n\n")
        llm_output = llm(message)
        tts(llm_output)
        time.sleep(2)
