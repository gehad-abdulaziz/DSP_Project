"""Shared settings for ALL parts. Edit only after telling the team."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
OUT_DIR = ROOT / "outputs"

# Input files provided by the instructor (copy them into data/)
AUDIO_PATH = DATA_DIR / "speech.wav"
IMAGE_PATH = DATA_DIR / "image.png"

# Reproducibility
SEED = 42

# Audio interference (Part 3 adds it, Part 4 removes it)
F_NOISE = 60          # Hz (50 for Egypt mains, or 60)
NOISY_WAV = OUT_DIR / "part3" / "noisy.wav"
FILTERED_WAV = OUT_DIR / "part4" / "filtered.wav"
