from scipy.interpolate import interp1d
import numpy as np


def interpolate_time_series(time_series, new_duration=None):
    duration = new_duration if new_duration is not None else len(time_series) - 1
    x_vals = np.linspace(0, duration, len(time_series))
    return interp1d(x_vals, time_series)


def get_onset_times_from_onset_density_array(onset_density_array, duration, density_multiplier=1,
                                             step_size="auto"):
    threshold = 1 / density_multiplier
    step_size = 0.1 / max(onset_density_array) if step_size == "auto" else step_size
    interpolated = interpolate_time_series(onset_density_array, duration)
    t = 0
    accumulator = 0
    onset_times = []
    while t < duration:
        accumulator += interpolated(t) * step_size
        while accumulator > threshold:
            onset_times.append(t)
            accumulator -= threshold
        t += step_size
    return onset_times
