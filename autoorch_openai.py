import openai
import json
from scamp_extensions.pitch import ScaleType

openai.api_key = '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'


preamble = """Make a JSON dictionary describing the given musical parameters for a
piece of music matching the following description: "{description}". Format your
reponse in the exact, full form of the example dictionary below, where "xxx" represents an
floating point rating from 0 to 1 and "sss" represents a scale chosen from ["diatonic", "whole_tone",
"pentatonic", "octatonic", "harmonic_minor", "melodic_minor", "blues", "chromatic"]. Only respond
with a dictionary in this exact format, with no extra comments or information.

For further context, "singability" refers to how smoothly the music should connect from note to
note, as would be natural for a singer. "dissonance" refers to how discordant or strident the
music should be. "pitch" refers to how high-pitched the music should be, with 
"pitch_range" indicating how much variation there should be in high and low. Similarly, "speed"
and "speed_range" indicate how fast the music should be and how much variety in fast and slow
there should be, respectively. A high "sonic_density" indicates big chords, while a low value
indicates single notes and possibly silence. "continuousness" refers to how much the music should
continue without stopping, with a low value representing more rests and phrase breaks. "regularity"
indicates how consistent and repetitive the music is rhythmically and in terms of volume. "resonance"
determines the use of sustain pedal on the piano and warm reverberation. Finally,
"scale" indicates the scale that should be used, which should also take into account the "dissonance"
parameter."""


prompt = """Here is the format:

{
    "singability": xxx,
    "dissonance": xxx
    "pitch": xxx,
    "pitch_range": xxx,
    "speed": xxx,
    "speed_range": xxx,
    "volume": xxx,
    "volume_range": xxx,
    "sonic_density": xxx,
    "continuousness": xxx,
    "regularity": xxx,
    "resonance": xxx,
    "scale": sss
}

Response:
"""

# Consider adding harmonic flux

def average_dicts(dicts):
    keys = set(x for d in dicts for x in d.keys())
    return {key: sum(d.get(key, 0) / len(dicts) for d in dicts) for key in keys}
    
_scale_names_to_types = {
    "diatonic": ScaleType.diatonic(),
    "whole_tone": ScaleType.whole_tone(),
    "pentatonic": ScaleType.pentatonic(),
    "octatonic": ScaleType.octatonic(),
    "harmonic_minor": ScaleType.harmonic_minor(),
    "melodic_minor": ScaleType.melodic_minor(),
    "blues": ScaleType.blues(),
    "chromatic": ScaleType.chromatic()
}

def get_music_dict(description):
#     print(f"Sending \"{description}\" to openai...", end=" ")
    completion = openai.ChatCompletion.create(
        model = 'gpt-3.5-turbo',
        messages = [{"role": "user", "content": preamble.format(description=description) + prompt}],
        temperature = 0,
        max_tokens = 512,
    )
    music_dict = json.loads(completion.choices[0].message["content"])
#     print("Response received:")
    music_dict["scale"] = _scale_names_to_types.get(music_dict["scale"], ScaleType.diatonic())
    return music_dict

if __name__ == "__main__":
    description = """Drunk man stumbling across the street"""
    print(get_music_dict(description))
    
# 
# content = response['choices'][0]['text']
# 
# for response in response['choices']:
#     print(response.text)
