import socket
import json
from autoorch import MusicParametrization
from autoorch_openai import get_music_dict
from scamp import Session
from scamp_extensions.pitch import ScaleType
import time
import random


with open("config.json", 'r') as config_file:
    config = json.load(config_file)
    

PORT = config["TCP Listening Port"]
IP_ADDRESS = config["TCP IP Address"]

# Create a TCP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.connect((IP_ADDRESS, PORT))

print("Connected to audience input terminal.")

s = Session().run_as_server()

s.timing_policy = "absolute"
s.synchronization_policy = "no synchronization"

piano = s.new_midi_part(config["MIDI device name"])

def play_tag(tonic):
    for pitch, volume in zip([tonic - 2, tonic - 12, tonic - 24], [0.5, 0.6, 0.7]):
        piano.play_note(pitch, volume, 1/12)
    piano.play_chord([tonic - 36, tonic - 24], 0.8, 5)


current_music_parametrization = MusicParametrization(
    {'singability': 0, 'dissonance': 0.3, 'pitch': 0.5, 'pitch_range': 0.7, 'speed': 0.1,
     'speed_range': 0, 'volume': 0.2, 'volume_range': 0.3, 'sonic_density': 0.3, 'continuousness': 0.9,
     'regularity': 1.0, 'scale': ScaleType.chromatic(), 'resonance': 0.8}
)

current_tonic = 62
current_music = None

def midi_listener(message):
    global current_music
    print(f"Received message at {message[:2]}")
    if list(message[:2]) == config["MIDI Start"] and message[2] > 0:
        piano.send_midi_cc(64, 1)
        s.fork(play_tag, args=(current_tonic, ))
        if current_music:
            current_music.kill()
        current_music = s.fork(current_music_parametrization.play, args=(piano, current_tonic))
    elif list(message[:2]) == config["MIDI Stop"] and message[2] > 0:
        if current_music:
            current_music.kill()
            current_music = None

s.register_midi_listener(config["MIDI Device Name"], midi_listener)

while True:
    description = server_socket.recv(1024).decode().strip()
    if description.lower() == config["Ending Phrase"].lower():
        print("Received ending phrase")
        break
    print(f"Received \"{description}\". Sending to Georg Philipp Telemann for consideration...")
    parameter_dict = get_music_dict(description)
    current_music_parametrization = MusicParametrization(parameter_dict)
    current_tonic = random.randrange(54, 66)
    print(f"Here's what he said: {parameter_dict}")
    if current_music:
        current_music.kill()
    current_music = s.fork(current_music_parametrization.play, args=(piano, current_tonic))
    with open(config["parameter_output_file"], 'w') as parameter_output_file:
        json.dump({k: v for k, v in parameter_dict.items() if k != "scale"}, parameter_output_file)

if current_music:
    current_music.kill()
s.fork(play_tag, args=(current_tonic, ))
s.wait(5)
s.kill()