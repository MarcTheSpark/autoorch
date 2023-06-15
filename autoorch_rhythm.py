import random
from scamp_extensions.utilities import remap, round_to_multiple

def rhythm_generator(speed, variability, smoothness, quantized=False):
    last_dur_unmapped = None
    while True:
        dur_unmapped = random.uniform(0.2 + speed * 0.8 - variability ** 2, 0.2 + speed * 0.8  + variability ** 2)
        if last_dur_unmapped:
            dur_unmapped = dur_unmapped * (1 - smoothness * 0.9) + last_dur_unmapped * (smoothness * 0.9)
        last_dur_unmapped = dur_unmapped
            
        dur = remap(dur_unmapped,
                    3, 0.07, 0, 1,
                    output_warp="exp")

        if quantized:
            yield round_to_multiple(dur, 0.0625) if dur < 0.15 else \
                  round_to_multiple(dur, 0.125) if dur < 0.3 else \
                  round_to_multiple(dur, 0.25) if dur < 1 else round_to_multiple(dur, 0.5)
        else:
            yield dur


if __name__ == '__main__':
    from scamp import *

    s = Session()

    piano = s.new_part("piano")

    for dur in rhythm_generator(0.8, 0.8, 0.2, quantized=False):
        print(dur)
    piano.play_note(60, 1.0, dur)
