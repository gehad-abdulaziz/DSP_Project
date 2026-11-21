# Multi-Domain Digital Signal Processing Project

Python project covering mathematical signals, audio, and images.

## Setup

    python -m venv .venv
    .\.venv\Scripts\Activate.ps1   (Windows PowerShell)
    source .venv/bin/activate      (Linux / macOS)
    pip install -r requirements.txt

Copy the provided files into `data/` as `speech.wav` and `image.png` (or edit `config.py`).

## Run

    python main.py        (all parts)
    python main.py 3 4    (selected parts)

Results (plots, WAV files) are saved in `outputs/part1 ... part6`.

## Team

| Part | Topic | Student |
|---|---|---|
| 1 | Mathematical Signal & DTFT | Gehad Abdelaziz |
| 2 | Convolution & Difference Equations | Nour Hatem |
| 3 | Audio Analysis | Mohamed khaled |
| 4 | Audio Filtering | Noa Ahmed|
| 5 | 2D Fourier & Image Filtering | Gehad Abdelaziz |
| 6 | Image Denoising & Evaluation | Hania Zaher |

## Notes

- Part 4 reads `outputs/part3/noisy.wav`, so run Part 3 first.
- Parts 1 and 2 generate their own signals and need no input files.
