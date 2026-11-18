# Multi-Domain Digital Signal Processing Project

Python project covering mathematical signals, audio, and images.

## Setup

    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install -r requirements.txt

Copy the provided files into `data/` as `speech.wav` and `image.png` (or edit `config.py`).

## Run

    python main.py        (all parts)
    python main.py 3 4    (selected parts)

Results (plots, WAV files) are saved in `outputs/part1 ... part6`.

## Team

| Part | Topic | Student |
|---|---|---|
| 1 | Mathematical Signal & DTFT | |
| 2 | Convolution & Difference Equations | |
| 3 | Audio Analysis | |
| 4 | Audio Filtering | |
| 5 | 2D Fourier & Image Filtering | |
| 6 | Image Denoising & Evaluation | |

## Notes

- Part 4 reads `outputs/part3/noisy.wav`, so run Part 3 first.