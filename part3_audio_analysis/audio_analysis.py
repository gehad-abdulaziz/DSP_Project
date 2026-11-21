# Part 3 - Audio Analysis
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import spectrogram

import config
from common.io_utils import out_dir, load_audio, save_audio
from common.plot_utils import save_fig

# ------------------------------------------------------------------
# Settings (change these to experiment)
# ------------------------------------------------------------------
SNR_DB = 10             # signal-to-interference ratio of noisy.wav (lower = louder hum)
FRAME_MS = 25           # spectrogram window length (typical for speech)
HOP_MS = 10             # step between two spectrogram windows
LONG_FRAME_MS = 100     # long window used in the window-length comparison
SHORT_FRAME_MS = 10     # short window used in the window-length comparison
ENERGY_FRACTION = 0.95  # "bandwidth" = frequency below which this share of the energy lies
DB_RANGE = 80           # dynamic range shown in the spectrogram plots, in dB
HUM_BAND_HZ = 2         # +/- band around F_NOISE used to measure the hum level


# ------------------------------------------------------------------
# Step 1: time domain
# ------------------------------------------------------------------
def time_axis(x, fs):
    """Time in seconds for every sample of x."""
    return np.arange(len(x)) / fs


def rms(x):
    return np.sqrt(np.mean(x ** 2))


# ------------------------------------------------------------------
# Step 2: spectrum
# ------------------------------------------------------------------
def magnitude_spectrum(x, fs):
    """One-sided FFT magnitude. A Hann window reduces spectral leakage.

    Returns the frequency axis in Hz and |X(f)| (the signal is real, so the
    negative frequencies only repeat the positive ones).
    """
    window = np.hanning(len(x))
    X = np.fft.rfft(x * window)
    f = np.fft.rfftfreq(len(x), d=1 / fs)       # f[k] = k * fs / N
    return f, np.abs(X)


def to_db(mag, ref):
    """Magnitude in dB relative to `ref` (0 dB = the reference level)."""
    return 20 * np.log10(mag / ref + 1e-12)


def dominant_frequency(f, mag, f_min=20):
    """Strongest frequency above f_min (ignores DC and very low rumble)."""
    keep = f >= f_min
    return f[keep][np.argmax(mag[keep])]


def energy_bandwidth(f, mag, fraction=ENERGY_FRACTION):
    """Frequency below which `fraction` of the total energy lies."""
    energy = np.cumsum(mag ** 2)
    return f[np.searchsorted(energy, fraction * energy[-1])]


def level_near(f, mag, f0, half_width=HUM_BAND_HZ):
    """Largest magnitude within f0 +/- half_width Hz."""
    band = (f >= f0 - half_width) & (f <= f0 + half_width)
    return mag[band].max()


# ------------------------------------------------------------------
# Step 3: spectrogram
# ------------------------------------------------------------------
def compute_spectrogram(x, fs, frame_ms, hop_ms=HOP_MS):
    """Short-time Fourier transform with a Hann window.

    Returns frequencies (Hz), times (s) and the power in linear scale.
    """
    nperseg = min(int(fs * frame_ms / 1000), len(x))
    noverlap = max(nperseg - int(fs * hop_ms / 1000), 0)
    f, t, Sxx = spectrogram(x, fs=fs, window="hann", nperseg=nperseg,
                            noverlap=noverlap, mode="psd")
    return f, t, Sxx


def draw_spectrogram(ax, f, t, Sxx, ref, title, f_max=None):
    """Draw a spectrogram in dB relative to `ref` (the loudest cell = 0 dB)."""
    db = 10 * np.log10(Sxx / ref + 1e-12)
    image = ax.pcolormesh(t, f, db, shading="auto", vmin=-DB_RANGE, vmax=0,
                          cmap="magma")
    ax.set_title(title)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Frequency (Hz)")
    if f_max is not None:
        ax.set_ylim(0, f_max)
    return image


# ------------------------------------------------------------------
# Step 4: add the interference
# ------------------------------------------------------------------
def add_interference(x, fs, f0, snr_db):
    """x + A*sin(2*pi*f0*t), with A chosen so that the SNR equals snr_db.

    The sinusoid has power A^2/2, the speech has power rms(x)^2, so
    SNR = rms^2 / (A^2/2)  ->  A = sqrt(2) * rms / 10^(SNR/20).
    """
    t = time_axis(x, fs)
    amplitude = np.sqrt(2) * rms(x) / 10 ** (snr_db / 20)
    return x + amplitude * np.sin(2 * np.pi * f0 * t), amplitude


# ------------------------------------------------------------------
# Figures
# ------------------------------------------------------------------
def plot_waveform(x, fs, path):
    fig, ax = plt.subplots()
    ax.plot(time_axis(x, fs), x, linewidth=0.6)
    ax.set_title("Part 3: speech signal in the time domain")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude (normalized)")
    ax.set_xlim(0, len(x) / fs)
    ax.grid(True)
    save_fig(fig, path)


def plot_spectrum(f, mag, f_dom, f_bw, path):
    """Full spectrum (dB, log frequency axis) and a linear zoom on 0-1 kHz."""
    db = to_db(mag, mag.max())
    fig, (ax_full, ax_zoom) = plt.subplots(2, 1, figsize=(10, 8))

    ax_full.semilogx(f[1:], db[1:])                 # skip f = 0 (log axis)
    ax_full.axvline(f_bw, color="red", linestyle="--", alpha=0.7,
                    label=f"{ENERGY_FRACTION:.0%} of the energy below {f_bw:.0f} Hz")
    ax_full.set_title("Magnitude spectrum of the speech (log frequency axis)")
    ax_full.set_xlabel("Frequency (Hz)")
    ax_full.set_ylabel("Magnitude (dB, 0 dB = peak)")
    ax_full.set_ylim(-DB_RANGE, 5)
    ax_full.grid(True, which="both", alpha=0.4)
    ax_full.legend()

    zoom = f <= 1000
    ax_zoom.plot(f[zoom], db[zoom])
    ax_zoom.axvline(f_dom, color="green", linestyle="--", alpha=0.7,
                    label=f"strongest peak at {f_dom:.0f} Hz")
    ax_zoom.set_title("Zoom on 0 - 1000 Hz (linear frequency axis)")
    ax_zoom.set_xlabel("Frequency (Hz)")
    ax_zoom.set_ylabel("Magnitude (dB, 0 dB = peak)")
    ax_zoom.set_xlim(0, 1000)
    ax_zoom.set_ylim(-DB_RANGE, 5)
    ax_zoom.grid(True)
    ax_zoom.legend()
    save_fig(fig, path)


def plot_clean_spectrogram(x, fs, path):
    f, t, Sxx = compute_spectrogram(x, fs, FRAME_MS)
    fig, ax = plt.subplots()
    image = draw_spectrogram(ax, f, t, Sxx, Sxx.max(),
                             f"Spectrogram of the speech ({FRAME_MS} ms Hann window, "
                             f"{HOP_MS} ms step)")
    fig.colorbar(image, ax=ax, label="Power (dB, 0 dB = loudest cell)")
    save_fig(fig, path)


def plot_clean_vs_noisy(clean, noisy, fs, f0, path):
    """Top: a short zoom in time. Bottom: both spectra near the hum frequency."""
    centre = np.argmax(np.abs(clean))                # loudest moment of the speech
    half = int(0.05 * fs)                            # +/- 50 ms around it
    seg = slice(max(centre - half, 0), min(centre + half, len(clean)))

    f, mag_clean = magnitude_spectrum(clean, fs)
    _, mag_noisy = magnitude_spectrum(noisy, fs)
    ref = mag_clean.max()                            # same reference for both curves

    fig, (ax_t, ax_f) = plt.subplots(2, 1, figsize=(10, 8))

    t = time_axis(clean, fs)
    ax_t.plot(t[seg], clean[seg], label="Clean")
    ax_t.plot(t[seg], noisy[seg], alpha=0.7, label=f"Noisy (+ {f0} Hz hum)")
    ax_t.set_title("Time domain: 100 ms around the loudest sample")
    ax_t.set_xlabel("Time (s)")
    ax_t.set_ylabel("Amplitude")
    ax_t.grid(True)
    ax_t.legend()

    zoom = f <= 300
    ax_f.plot(f[zoom], to_db(mag_clean, ref)[zoom], label="Clean")
    ax_f.plot(f[zoom], to_db(mag_noisy, ref)[zoom], alpha=0.8, label="Noisy")
    ax_f.axvline(f0, color="red", linestyle="--", alpha=0.6, label=f"{f0} Hz")
    ax_f.set_title(f"Spectrum 0 - 300 Hz: the interference is a narrow spike at {f0} Hz")
    ax_f.set_xlabel("Frequency (Hz)")
    ax_f.set_ylabel("Magnitude (dB, 0 dB = peak of clean)")
    ax_f.set_xlim(0, 300)
    ax_f.grid(True)
    ax_f.legend()
    save_fig(fig, path)


def plot_window_length(noisy, fs, f0, path):
    """Extra: a long window resolves the hum line, a short one smears it."""
    short = compute_spectrogram(noisy, fs, SHORT_FRAME_MS)
    long_ = compute_spectrogram(noisy, fs, LONG_FRAME_MS)
    ref = max(short[2].max(), long_[2].max())        # same colour scale for both

    fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    for ax, (f, t, Sxx), ms in zip(axes, (short, long_),
                                   (SHORT_FRAME_MS, LONG_FRAME_MS)):
        res = 1000 / ms
        image = draw_spectrogram(ax, f, t, Sxx, ref,
                                 f"Noisy signal, {ms} ms window "
                                 f"(resolution about {res:.0f} Hz)", f_max=400)
        ax.axhline(f0, color="cyan", linestyle="--", alpha=0.6, linewidth=0.8)
        ax.set_xlabel("")
    axes[-1].set_xlabel("Time (s)")
    fig.colorbar(image, ax=axes, label="Power (dB)")
    fig.savefig(path, bbox_inches="tight")           # tight_layout conflicts with colorbar
    plt.close(fig)


# ------------------------------------------------------------------
# Main entry point (called by main.py)
# ------------------------------------------------------------------
def run():
    print("Part 3: Audio Analysis")
    if not config.AUDIO_PATH.exists():
        print(f"  Audio file not found: {config.AUDIO_PATH}")
        print("  Copy the provided audio into data/ (see config.py) and run again.")
        return

    out = out_dir(3)

    # 1) load + time domain
    fs, x = load_audio()
    print(f"  Sampling rate: {fs} Hz   Samples: {len(x)}   Duration: {len(x) / fs:.2f} s")
    print(f"  Peak: {np.max(np.abs(x)):.3f}   RMS: {rms(x):.4f}")
    plot_waveform(x, fs, out / "01_waveform.png")

    # 2) spectrum
    f, mag = magnitude_spectrum(x, fs)
    f_dom = dominant_frequency(f, mag)
    f_bw = energy_bandwidth(f, mag)
    print(f"  Strongest spectral peak: {f_dom:.1f} Hz")
    print(f"  {ENERGY_FRACTION:.0%} of the energy is below {f_bw:.0f} Hz "
          f"(Nyquist = {fs / 2:.0f} Hz)")
    plot_spectrum(f, mag, f_dom, f_bw, out / "02_spectrum.png")

    # 3) spectrogram
    plot_clean_spectrogram(x, fs, out / "03_spectrogram.png")

    # 4) add the interference and save noisy.wav (Part 4 reads this file)
    noisy, amplitude = add_interference(x, fs, config.F_NOISE, SNR_DB)
    print(f"  Added a {config.F_NOISE} Hz sinusoid, amplitude {amplitude:.4f} "
          f"(SNR = {SNR_DB} dB)")
    if np.max(np.abs(noisy)) > 1:
        print("  Note: noisy signal exceeds 1.0, save_audio() scales it down to avoid clipping")
    save_audio(config.NOISY_WAV, fs, noisy)

    # extras: compare clean and noisy
    _, mag_noisy = magnitude_spectrum(noisy, fs)
    rise = to_db(level_near(f, mag_noisy, config.F_NOISE),
                 level_near(f, mag, config.F_NOISE))
    print(f"  Level at {config.F_NOISE} Hz rose by {rise:.1f} dB after adding the hum")
    plot_clean_vs_noisy(x, noisy, fs, config.F_NOISE, out / "04_clean_vs_noisy.png")
    plot_window_length(noisy, fs, config.F_NOISE, out / "05_window_length.png")

    print(f"  Plots saved in: {out}")
    print(f"  Noisy audio saved as: {config.NOISY_WAV}")


if __name__ == "__main__":
    run()
