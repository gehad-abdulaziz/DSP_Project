"""Loading / saving helpers shared by all parts."""
from pathlib import Path

import cv2
import numpy as np
from scipy.io import wavfile

import config


def out_dir(part: int) -> Path:
    """Returns outputs/part<N>/ and creates it if needed."""
    p = config.OUT_DIR / f"part{part}"
    p.mkdir(parents=True, exist_ok=True)
    return p


def load_audio(path=config.AUDIO_PATH):
    """Returns (fs, x) with x as mono float64 in [-1, 1]."""
    fs, x = wavfile.read(path)
    if x.dtype == np.uint8:
        x = (x.astype(np.float64) - 128) / 128
    elif np.issubdtype(x.dtype, np.integer):
        x = x.astype(np.float64) / np.iinfo(x.dtype).max
    else:
        x = x.astype(np.float64)
    if x.ndim > 1:
        x = x.mean(axis=1)
    return fs, x


def save_audio(path, fs, x):
    """Saves float signal as 16-bit WAV (normalizes only if it clips)."""
    x = np.asarray(x, dtype=np.float64)
    peak = np.max(np.abs(x))
    if peak > 1:
        x = x / peak
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    wavfile.write(path, fs, (x * 32767).astype(np.int16))


def load_gray_image(path=config.IMAGE_PATH):
    """Returns grayscale image as float64 array in [0, 255]."""
    img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Could not read image: {path}")
    return img.astype(np.float64)