import socket
import json
from autoorch import MusicParametrization
from autoorch_openai import get_music_dict
from scamp import Session
from scamp_extensions.pitch import ScaleType


with open("config.json", 'r') as config_file:
    config = json.load(config_file)
    

PORT = config["TCP Listening Port"]
IP_ADDRESS = config["TCP IP Address"]

# Create a TCP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.connect((IP_ADDRESS, PORT))
print("Connected to audience input terminal.")

s = Session().run_as_server()

piano = s.new_midi_part(config["MIDI device name"])

background_music_parametrization = MusicParametrization(
    {'singability': 0, 'dissonance': 0.3, 'pitch': 0.5, 'pitch_range': 0.7, 'speed': 0.1,
     'speed_range': 0, 'volume': 0.2, 'volume_range': 0.3, 'sonic_density': 0.3, 'continuousness': 0.9,
     'regularity': 1.0, 'scale': ScaleType.chromatic(), 'resonance': 0.8}
)


current_music = s.fork(background_music_parametrization.play, args=(piano, ))

while True:
    description = server_socket.recv(1024).decode().strip()
    print(f"Received \"{description}\". Sending to Georg Philipp Telemann for consideration...")
    parameter_dict = get_music_dict(description)
    new_music_parametrization = MusicParametrization(parameter_dict)
    print(f"Here's what he said: {parameter_dict}")
    current_music.kill()
    current_music = s.fork(new_music_parametrization.play, args=(piano, ))
    with open(config["parameter_output_file"], 'w') as parameter_output_file:
        json.dump({k: v for k, v in parameter_dict.items() if k != "scale"}, parameter_output_file)