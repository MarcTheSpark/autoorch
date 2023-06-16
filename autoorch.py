"""
Improve pedaling
Fix rhythmic regularity! Might need multiple cases, because it's not working that well right now
Fix the do not play probability
harmonic flux?
Make consonance apply to consecutive notes too
"""
from scamp import *
from scamp_extensions.pitch import Scale, ScaleType
from dataclasses import dataclass
from scamp_extensions.utilities import remap, cyclic_slice
from numpy.fft import irfft
import numpy as np
import random
import math
import cmath
from autoorch_rhythm import rhythm_generator
from autoorch_openai import get_music_dict
from autoorch_pitch import measure_chord_consonance
import json
import itertools


class MusicParametrization:
    
    scales_by_dissonance = [
        Scale.pentatonic(60),
        Scale.from_pitches([60, 62, 64, 66, 67, 69, 72]),
        Scale.from_pitches([60, 62, 64, 66, 67, 69, 70, 72]),
        Scale.from_pitches([60, 62, 63, 66, 67, 69, 70, 72]),
        Scale.from_pitches([60, 61, 63, 64, 66, 67, 69, 70, 72]),
        Scale.from_pitches([60, 61, 62, 63, 64, 66, 67, 68, 69, 70, 72]),
        Scale.chromatic(60)
    ]

    
    def __init__(self, parameters):
        self.parameters = parameters
        self.pitch_contour = MusicParametrization.get_contour(1 - parameters['singability'],
                                                              parameters['pitch'],
                                                              parameters['pitch_range'],
                                                              (21, 108))
        self.volume_contour = MusicParametrization.get_contour(1 - parameters['regularity'],
                                                              parameters['volume'],
                                                              parameters['volume_range'],
                                                              (0.2, 0.9))
        self.rhythm_generator = rhythm_generator(self.parameters['speed'],
                                                 self.parameters['speed_range'],
                                                 self.parameters['regularity'])
        if self.parameters['regularity'] > 2/3:
            loop_length = int((1.2 / self.parameters['regularity']) ** 2)
            self.rhythm_generator = itertools.cycle(itertools.islice(self.rhythm_generator, loop_length))  
            
        

    @staticmethod
    def get_contour(unpredictability, center, width, output_range, length=255):
        amp_spectrum = Envelope([1, 1, 0, 0],
                                [unpredictability ** 2 * 0.2 + 0.01, unpredictability ** 2 * 0.2 + 0.01, 0.8])
        contour = irfft([0.0] + [random.uniform(0, amp_spectrum.value_at(i / 255)) *
                                 cmath.exp(random.uniform(-math.pi, math.pi) * 1j) for i in range(255)])
        contour /= np.max(contour)
        
        contour = center + width / 2 * contour      
        if (max_val := np.max(contour)) > 1:
            contour[contour > center] = (contour[contour > center] - center) * (1 - center) / (max_val - center) + center
        if (min_val := np.min(contour)) < 0:
            contour[contour < center] = (contour[contour < center] - center) * (0 - center) / (min_val - center) + center
         
        contour = contour * (output_range[1] - output_range[0]) + output_range[0]
 
        return contour
    
    def play(self, inst: ScampInstrument):
        scale = Scale(self.parameters['scale'], random.randrange(54, 66))
        inst.send_midi_cc(64, 0)
        while True:
            for contour_index in range(0, len(self.pitch_contour), 8):
                if random.random() < (self.parameters['continuousness'] + self.parameters['resonance']) / 2:
                    inst.send_midi_cc(64, self.parameters['resonance'] ** 0.5)
                else:
                    inst.send_midi_cc(64, 0)
                pitch = scale.round(self.pitch_contour[contour_index])
                if random.random() > (self.parameters['sonic_density'] + self.parameters['speed'] + self.parameters['continuousness']) / 2:
                    wait(next(self.rhythm_generator))
                elif random.random() < self.parameters['sonic_density'] ** 0.8:
                    num_chord_tones = int(remap(self.parameters['sonic_density'] - 0.4, 2, 6, 0, 1))
                    degree = int(scale.pitch_to_degree(pitch))
                    chord_options = [scale[sorted(random.sample(range(degree - 3 - int(self.parameters['pitch_range'] ** 1.5 * 8),
                                                                    degree + 3 + int(self.parameters['pitch_range'] ** 1.5 * 8)),
                                                              num_chord_tones))]
                                     for _ in range(30)]
                    chord_options.sort(key=measure_chord_consonance, reverse=True)
                    dithered_dissonance = min(1, max(0, self.parameters['dissonance'] + random.uniform(-0.1, 0.1)))
                    chord = chord_options[int(dithered_dissonance * len(chord_options) * 0.999)]
                    inst.play_chord(chord, self.volume_contour[contour_index], next(self.rhythm_generator))
                else:
                    inst.play_note(pitch, self.volume_contour[contour_index], next(self.rhythm_generator))


# pedal: continousness, sonic density, resonance

if __name__ == '__main__':
    
    s = Session().run_as_server()

    piano = s.new_midi_part("MIDI-Through")

    background_music_parametrization = MusicParametrization(
        {'singability': 0, 'dissonance': 0.3, 'pitch': 0.5, 'pitch_range': 0.7, 'speed': 0.1,
         'speed_range': 0, 'volume': 0.2, 'volume_range': 0.3, 'sonic_density': 0.3, 'continuousness': 0.9,
         'regularity': 1.0, 'scale': ScaleType.chromatic(), 'resonance': 0.8}
    )


    current_music = s.fork(background_music_parametrization.play, args=(piano, ))

    while True:
        description = input("What kind of music do you want to hear? ")
        print(f"Sending \"{description}\" to Georg Philipp Telemann for consideration...")
        new_music_parametrization = MusicParametrization(get_music_dict(description))
        
        print(f"Here's what he said: {new_music_parametrization.parameters}")
        current_music.kill()
        current_music = s.fork(new_music_parametrization.play, args=(piano, ))

