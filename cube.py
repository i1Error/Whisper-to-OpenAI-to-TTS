import io
import requests
from pydub import AudioSegment
from pydub.playback import play
import speech_recognition as sr
import queue
import tempfile
import os
import threading
import click
import torch
import numpy as np
import openai
import json

EL_key = "Your EL_key"
EL_voice = "Your EL_voice"
OAI_key = "Your OAI_key"
 
@click.command()
@click.option("--verbose", default=False, help="Whether to print verbose output", is_flag=True,type=bool)
@click.option("--energy", default=300, help="Energy level for mic to detect", type=int)
@click.option("--dynamic_energy", default=False,is_flag=True, help="Flag to enable dynamic engergy", type=bool)
@click.option("--pause", default=0.8, help="Pause time before entry ends", type=float)
@click.option("--save_file",default=True, help="Flag to save file", is_flag=True,type=bool)

def main(verbose, energy, pause, dynamic_energy, save_file):
    openai.api_key = OAI_key
    convhistory = []
    temp_dir = tempfile.mkdtemp() if save_file else None
    audio_queue = queue.Queue()
    result_queue = queue.Queue()    
    
    threading.Thread(target=record_audio, args=(audio_queue, energy, pause, dynamic_energy, save_file, temp_dir)).start()
    threading.Thread(target=transcribe_forever, args=(audio_queue, result_queue, verbose, save_file, convhistory)).start()
    while True:
        whisper_result = result_queue.get()
        print(whisper_result)       

def record_audio(audio_queue, energy, pause, dynamic_energy, save_file, temp_dir):
    r = sr.Recognizer()
    r.energy_threshold = energy
    r.pause_threshold = pause
    r.dynamic_energy_threshold = dynamic_energy

    with sr.Microphone(sample_rate=16000) as source:
        print("Say something! If you want to talk with Cube the prompt must contain Cube")
        i = 0
        while True:
            audio = r.listen(source)

            data = io.BytesIO(audio.get_wav_data())
            audio_clip = AudioSegment.from_file(data)
            if save_file and temp_dir:
                filename = os.path.join(temp_dir, f"temp{i}.wav")
                audio_clip.export(filename, format="wav")
                audio_data = open(filename, 'rb') 
            else:
                audio_data = io.BytesIO(data.getvalue())

            audio_queue.put_nowait(audio_data)
            i += 1

def transcribe_forever(audio_queue, result_queue, verbose, save_file, convhistory):
    is_typing = False 
    
    while True:
        if not is_typing:
            audio_data = audio_queue.get()
            result = openai.Audio.transcribe(api_key=OAI_key, model="whisper-1", file=audio_data)
            predicted_text = result["text"]
            result_queue.put_nowait("User: " + predicted_text)
            
            if "stop cube" in predicted_text.lower():
                break
            
            if "cube" in predicted_text.lower():
                llm(predicted_text, convhistory)  

            if "print conversation" in predicted_text.lower():
                print("\n\nconvhistory:\n" + "".join(convhistory)+"\n\n")
                
            if "switch to typing" in predicted_text.lower():
                is_typing = True
                print("Switching to typing mode. Type 'Switch to talking' to switch back to talking mode.")
            
            if save_file:
                audio_data.close()  
                os.remove(audio_data.name)
                    
        else:
            mpro = input()
            if mpro.lower() == "switch to talking":
                is_typing = False
                print("Switching to talking mode.")

            if "stop cube" in predicted_text.lower():
                break
            
            if "cube" in predicted_text.lower():
                llm(predicted_text, convhistory)  

            if "print conversation" in predicted_text.lower():
                print("\n\nconvhistory:\n" + "".join(convhistory)+"\n\n")
            else:
                llm(mpro, convhistory)

 
def llm(message, convhistory):
    openai.api_key = OAI_key
    gptprompt= f"\n\n{convhistory}\n\nThis is how a smart Person would responded in a conversation. That person would respond in a tense manner and gives advice and information.\n\The Person would talk about the message and would elaborate on it as well. The Person will answer in short sentences. You will behave like such a person\n#########Message:\n{message}\nEnd Message#########\n"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": gptprompt}]
    )

    json_object = json.loads(str(response))
    response_text = json_object['choices'][0]['message']['content']
       
    print("Cube: " + response_text)      
    audio_data = tts(response_text)
    play(AudioSegment.from_file(io.BytesIO(audio_data)))
    
    convhistory.append("User: " + message + "\n")
    convhistory.append("Cube: " + response_text + "\n") 
    return response_text

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
    response = requests.post(url, headers=headers, json=data)
    return response.content

main()

#TODO
#include the webpage for custimazation
