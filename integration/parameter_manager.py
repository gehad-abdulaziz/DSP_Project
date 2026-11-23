"""
Parameter Manager — Centralizes all configurable DSP parameters.

Each part has a dictionary of parameters with:
  - default: the original hardcoded value from the source code
  - type: 'int', 'float', 'tuple_int', 'tuple_float'
  - min/max: validation bounds
  - step: increment for sliders
  - label: human-readable name
  - help: tooltip text
"""

PART_PARAMETERS = {
    1: {
        "FS": {
            "default": 1000, "type": "int", "min": 100, "max": 10000, "step": 100,
            "label": "Sampling Frequency (Hz)",
            "help": "Number of samples per second. Higher values give better frequency resolution."
        },
        "N": {
            "default": 64, "type": "int", "min": 8, "max": 512, "step": 8,
            "label": "Number of Samples",
            "help": "Length of the discrete-time signal. More samples → narrower DTFT peaks."
        },
        "F1": {
            "default": 100, "type": "int", "min": 1, "max": 5000, "step": 10,
            "label": "Frequency 1 (Hz)",
            "help": "Frequency of the first sinusoid component."
        },
        "F2": {
            "default": 250, "type": "int", "min": 1, "max": 5000, "step": 10,
            "label": "Frequency 2 (Hz)",
            "help": "Frequency of the second sinusoid component."
        },
        "A1": {
            "default": 1.0, "type": "float", "min": 0.01, "max": 5.0, "step": 0.1,
            "label": "Amplitude 1",
            "help": "Amplitude of the first sinusoid."
        },
        "A2": {
            "default": 0.6, "type": "float", "min": 0.01, "max": 5.0, "step": 0.1,
            "label": "Amplitude 2",
            "help": "Amplitude of the second sinusoid."
        },
        "NOISE_STD": {
            "default": 0.3, "type": "float", "min": 0.0, "max": 2.0, "step": 0.05,
            "label": "Noise Std Dev",
            "help": "Standard deviation of the additive Gaussian noise."
        },
        "NUM_FREQ_POINTS": {
            "default": 512, "type": "int", "min": 64, "max": 2048, "step": 64,
            "label": "Frequency Grid Points",
            "help": "Number of frequency evaluation points for the DTFT."
        },
    },
    2: {
        "FS": {
            "default": 1000, "type": "int", "min": 100, "max": 10000, "step": 100,
            "label": "Sampling Frequency (Hz)",
            "help": "Sampling rate used for the test signal."
        },
        "N": {
            "default": 200, "type": "int", "min": 20, "max": 2000, "step": 20,
            "label": "Number of Samples",
            "help": "Length of the noisy test sinusoid."
        },
        "F_SIGNAL": {
            "default": 20, "type": "int", "min": 1, "max": 500, "step": 1,
            "label": "Signal Frequency (Hz)",
            "help": "Frequency of the useful sinusoid embedded in noise."
        },
        "NOISE_STD": {
            "default": 0.5, "type": "float", "min": 0.0, "max": 3.0, "step": 0.1,
            "label": "Noise Std Dev",
            "help": "Standard deviation of the additive Gaussian noise."
        },
        "M_VALUES": {
            "default": (3, 5, 11), "type": "tuple_int",
            "label": "Moving Average Windows (M)",
            "help": "Window lengths for the moving average filter comparison."
        },
        "M_DEMO": {
            "default": 5, "type": "int", "min": 2, "max": 50, "step": 1,
            "label": "Demo Window Length (M)",
            "help": "Window length for the time-vs-frequency-domain comparison."
        },
        "A_STABLE": {
            "default": 0.8, "type": "float", "min": 0.01, "max": 0.99, "step": 0.01,
            "label": "Stable Coefficient (a)",
            "help": "|a| < 1: impulse response decays."
        },
        "A_UNSTABLE": {
            "default": 1.2, "type": "float", "min": 1.01, "max": 3.0, "step": 0.01,
            "label": "Unstable Coefficient (a)",
            "help": "|a| > 1: impulse response grows."
        },
        "NUM_Y": {
            "default": 40, "type": "int", "min": 10, "max": 200, "step": 5,
            "label": "Diff. Eq. Output Samples",
            "help": "Number of impulse response samples for the difference equation."
        },
    },
    3: {
        "SNR_DB": {
            "default": 10, "type": "int", "min": -10, "max": 50, "step": 1,
            "label": "SNR (dB)",
            "help": "Signal-to-interference ratio. Lower = louder hum."
        },
        "FRAME_MS": {
            "default": 25, "type": "int", "min": 5, "max": 200, "step": 5,
            "label": "Frame Length (ms)",
            "help": "Spectrogram window length (typical speech: 25 ms)."
        },
        "HOP_MS": {
            "default": 10, "type": "int", "min": 1, "max": 100, "step": 1,
            "label": "Hop Size (ms)",
            "help": "Step between spectrogram windows."
        },
        "LONG_FRAME_MS": {
            "default": 100, "type": "int", "min": 20, "max": 500, "step": 10,
            "label": "Long Frame (ms)",
            "help": "Long window for the resolution comparison."
        },
        "SHORT_FRAME_MS": {
            "default": 10, "type": "int", "min": 2, "max": 50, "step": 1,
            "label": "Short Frame (ms)",
            "help": "Short window for the resolution comparison."
        },
        "ENERGY_FRACTION": {
            "default": 0.95, "type": "float", "min": 0.5, "max": 0.999, "step": 0.01,
            "label": "Energy Fraction",
            "help": "Bandwidth threshold: frequency below which this share of energy lies."
        },
        "F_NOISE": {
            "default": 60, "type": "int", "min": 10, "max": 500, "step": 1,
            "label": "Interference Frequency (Hz)",
            "help": "Frequency of the mains-hum interference (50 or 60 Hz typical)."
        },
    },
    4: {
        "NOTCH_FREQUENCY_HZ": {
            "default": 60, "type": "int", "min": 10, "max": 500, "step": 1,
            "label": "Notch Frequency (Hz)",
            "help": "Frequency to remove with the notch filter."
        },
        "POLE_RADIUS": {
            "default": 0.999, "type": "float", "min": 0.9, "max": 0.9999, "step": 0.001,
            "label": "Pole Radius",
            "help": "Closer to 1 → narrower, sharper notch."
        },
        "ZOOM_BANDWIDTH_HZ": {
            "default": 30, "type": "int", "min": 5, "max": 200, "step": 5,
            "label": "Zoom Bandwidth (Hz)",
            "help": "Spectrum zoom range around the interference."
        },
        "TIME_ZOOM_SECONDS": {
            "default": 0.10, "type": "float", "min": 0.01, "max": 1.0, "step": 0.01,
            "label": "Time Zoom (seconds)",
            "help": "Duration of the waveform zoom comparison."
        },
    },
    5: {
        "CUTOFF": {
            "default": 30, "type": "int", "min": 1, "max": 200, "step": 1,
            "label": "Cutoff Radius (px)",
            "help": "Radius of the circular frequency-domain mask in pixels."
        },
        "RADII": {
            "default": (10, 30, 60), "type": "tuple_int",
            "label": "Comparison Radii",
            "help": "Radii compared in the effect-of-radius figure."
        },
    },
    6: {
        "AMPLITUDE": {
            "default": 50, "type": "int", "min": 1, "max": 200, "step": 5,
            "label": "Noise Amplitude",
            "help": "Strength of the periodic noise stripes (gray levels)."
        },
        "U0": {
            "default": 60, "type": "int", "min": 1, "max": 200, "step": 1,
            "label": "Horizontal Freq (u₀)",
            "help": "Noise frequency: cycles across the image width."
        },
        "V0": {
            "default": 40, "type": "int", "min": 1, "max": 200, "step": 1,
            "label": "Vertical Freq (v₀)",
            "help": "Noise frequency: cycles across the image height."
        },
        "NOTCH_RADIUS": {
            "default": 5, "type": "int", "min": 0, "max": 50, "step": 1,
            "label": "Notch Radius (px)",
            "help": "Radius of each notch hole in the frequency mask."
        },
        "RADII": {
            "default": (0, 2, 5, 10, 20, 40), "type": "tuple_int",
            "label": "Radius Study Values",
            "help": "Radii compared in the effect-of-radius study."
        },
    },
}


def get_defaults(part_num: int) -> dict:
    """Return a dict of {param_name: default_value} for a given part."""
    return {k: v["default"] for k, v in PART_PARAMETERS[part_num].items()}


def validate_params(part_num: int, params: dict) -> dict:
    """Clamp numerical values to their valid range. Returns validated copy."""
    schema = PART_PARAMETERS[part_num]
    validated = {}
    for key, val in params.items():
        if key not in schema:
            validated[key] = val
            continue
        s = schema[key]
        if s["type"] in ("int", "float") and "min" in s and "max" in s:
            val = max(s["min"], min(s["max"], val))
        validated[key] = val
    return validated
