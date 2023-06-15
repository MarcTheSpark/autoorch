import itertools


def interval_consonance(p1, p2):
    if abs(p1 - p2) % 12 in [0, 3, 4, 5, 7, 8, 9]:
        return True
    else:
        return False

def interval_imperfect_consonance(p1, p2):
    if abs(p1 - p2) % 12 in [3, 4, 8, 9]:
        return True
    else:
        return False

def measure_chord_consonance(pitches):
    consonant_count = 0
    total_count = 0
    for pair in itertools.combinations(pitches, 2):
        consonant_count += interval_consonance(*pair) / 2 + interval_imperfect_consonance(*pair) / 2
        total_count += 1
    return consonant_count / total_count
