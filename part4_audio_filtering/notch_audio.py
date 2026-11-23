
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import lfilter, freqz

import config
from common.io_utils import out_dir
from common.plot_utils import save_fig


NOTCH_FREQUENCY_HZ = config.F_NOISE
POLE_RADIUS = 0.999                 
ZOOM_BANDWIDTH_HZ = 30              
TIME_ZOOM_SECONDS = 0.10           


#WAV loading
def read_wav_mono_or_stereo(path):

    fs, data = wavfile.read(path)

    if np.issubdtype(data.dtype, np.integer):
        info = np.iinfo(data.dtype)
        scale = float(max(abs(info.min), abs(info.max)))
        audio = data.astype(np.float64) / scale
    else:
        audio = data.astype(np.float64)

    if audio.ndim not in (1, 2):
        raise ValueError(f"Unsupported audio shape: {audio.shape}")

    return fs, audio


def write_float_wav(path, fs, audio):
    audio = np.asarray(audio, dtype=np.float64)
    audio = np.clip(audio, -1.0, 1.0)
    wavfile.write(str(path), fs, audio.astype(np.float32))


#calculate the second-order notch coefficients
def calculate_notch_coefficients(fs, f0, radius=POLE_RADIUS):
    
    if not 0 < f0 < fs / 2:
        raise ValueError("Invalid notch frequency.")

    if not 0 < radius < 1:
        raise ValueError("Radius must be between 0 and 1.")

    w0 = 2.0 * np.pi * f0 / fs
    c = np.cos(w0)

    b0 = 1.0
    b1 = -2.0 * c
    b2 = 1.0

    a0 = 1.0
    a1 = -2.0 * radius * c
    a2 = radius ** 2

    gain = (a0 - a1 + a2) / (b0 - b1 + b2)

    b = gain * np.array([b0, b1, b2], dtype=np.float64)
    a = np.array([a0, a1, a2], dtype=np.float64)

    return w0, b, a, gain



#apply the same IIR notch filter to every channel
def apply_notch_filter(audio, b, a):
    if audio.ndim == 1:
        return lfilter(b, a, audio)

    filtered = np.empty_like(audio, dtype=np.float64)
    for channel in range(audio.shape[1]):
        filtered[:, channel] = lfilter(b, a, audio[:, channel])
    return filtered


def remove_edge_clicks(audio, fs, fade_ms=200):
    audio = audio.copy().astype(np.float64)

    fade_samples = int(fs * fade_ms / 1000)

    if fade_samples <= 1 or len(audio) < 2 * fade_samples:
        return audio

    fade_in = 0.5 - 0.5 * np.cos(
        np.linspace(0, np.pi, fade_samples)
    )

    fade_out = 0.5 + 0.5 * np.cos(
        np.linspace(0, np.pi, fade_samples)
    )

    if audio.ndim == 1:
        audio[:fade_samples] *= fade_in
        audio[-fade_samples:] *= fade_out

    else:
        audio[:fade_samples] *= fade_in[:, None]
        audio[-fade_samples:] *= fade_out[:, None]

    return audio


#convert to mono analysis signal
def mono_for_analysis(audio):
    if audio.ndim == 1:
        return audio
    return np.mean(audio, axis=1)

#convert sample to second
def time_axis(audio, fs):
    return np.arange(len(audio)) / fs

#convert time domain to frequency domain
def magnitude_spectrum(audio, fs):
    """One-sided (positive only) Hann-windowed magnitude spectrum."""
    x = mono_for_analysis(audio)
    window = np.hanning(len(x))
    spectrum = np.fft.rfft(x * window)
    frequencies = np.fft.rfftfreq(len(x), d=1.0 / fs)
    magnitude = np.abs(spectrum)
    return frequencies, magnitude

# measure band rms 
def band_rms_near_frequency(audio, fs, f0, half_width=2.0):

    frequencies, magnitude = magnitude_spectrum(audio, fs)

    band = (frequencies >= f0 - half_width) & (frequencies <= f0 + half_width)

    if not np.any(band):
        return 0.0
    return float(np.sqrt(np.mean(magnitude[band] ** 2)))

# measure noise db before and after filter 
def attenuation_db(before_level, after_level):
    eps = 1e-12
    return 20.0 * np.log10((before_level + eps) / (after_level + eps))


# Step 5: plots
#plot time
def plot_waveform_comparison(noisy, filtered, fs, path):
    x_noisy = mono_for_analysis(noisy)
    x_filtered = mono_for_analysis(filtered)
    count = min(len(x_noisy), int(TIME_ZOOM_SECONDS * fs))
    t = np.arange(count) / fs

    fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
    axes[0].plot(t, x_noisy[:count], linewidth=0.7)
    axes[0].set_title("Noisy audio waveform")
    axes[0].set_ylabel("Amplitude")
    axes[0].grid(True)

    axes[1].plot(t, x_filtered[:count], linewidth=0.7, color="tab:green")
    axes[1].set_title("Filtered audio waveform")
    axes[1].set_xlabel("Time (s)")
    axes[1].set_ylabel("Amplitude")
    axes[1].grid(True)

    fig.suptitle("Part 4: waveform before and after notch filtering")
    fig.tight_layout()
    save_fig(fig, path)

# plot frequency
def plot_spectrum_comparison(noisy, filtered, fs, f0, path):
    f_before, mag_before = magnitude_spectrum(noisy, fs)
    f_after, mag_after = magnitude_spectrum(filtered, fs)

    ref = max(float(mag_before.max()), float(mag_after.max()), 1e-12)
    before_db = 20 * np.log10(mag_before / ref + 1e-12)
    after_db = 20 * np.log10(mag_after / ref + 1e-12)

    fig, axes = plt.subplots(2, 1, figsize=(11, 8))
    axes[0].plot(f_before, before_db, label="Noisy")
    axes[0].plot(f_after, after_db, label="Filtered", alpha=0.85)
    axes[0].axvline(f0, color="red", linestyle="--", label=f"Notch frequency = {f0:g} Hz")
    axes[0].set_xlim(0, min(2000, fs / 2))
    axes[0].set_ylim(-100, 5)
    axes[0].set_title("Full spectrum comparison")
    axes[0].set_xlabel("Frequency (Hz)")
    axes[0].set_ylabel("Magnitude (dB)")
    axes[0].grid(True)
    axes[0].legend()

    axes[1].plot(f_before, before_db, label="Noisy")
    axes[1].plot(f_after, after_db, label="Filtered", alpha=0.85)
    axes[1].axvline(f0, color="red", linestyle="--", label=f"{f0:g} Hz")
    axes[1].set_xlim(max(0, f0 - ZOOM_BANDWIDTH_HZ),
                    min(fs / 2, f0 + ZOOM_BANDWIDTH_HZ))
    axes[1].set_ylim(-100, 5)
    axes[1].set_title(f"Zoom around the {f0:g} Hz interference")
    axes[1].set_xlabel("Frequency (Hz)")
    axes[1].set_ylabel("Magnitude (dB)")
    axes[1].grid(True)
    axes[1].legend()

    fig.tight_layout()
    save_fig(fig, path)


#plot filter
def plot_filter_response(b, a, fs, f0, path):
    frequencies = np.linspace(0, min(2000, fs / 2), 20001)

    w, response = freqz(
        b,
        a,
        worN=2 * np.pi * frequencies / fs
    )

    magnitude_db = 20 * np.log10(
        np.maximum(np.abs(response), 1e-12)
    )

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(frequencies, magnitude_db)

    ax.axvline(
        f0,
        color="red",
        linestyle="--",
        label=f"Notch at {f0:g} Hz"
    )

    ax.set_xlim(0, min(2000, fs / 2))
    ax.set_ylim(-100, 5)
    ax.set_title("Second-order IIR Notch Filter frequency response")
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Gain (dB)")
    ax.grid(True)
    ax.legend()

    save_fig(fig, path)
    
# zero   
def plot_pole_zero(b, a, path):
    zeros = np.roots(b)
    poles = np.roots(a)
    stable = bool(np.all(np.abs(poles) < 1))

    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    theta = np.linspace(0, 2 * np.pi, 400)

    for ax in axes:
        ax.plot(np.cos(theta), np.sin(theta), "k--", linewidth=0.8, label="Unit circle")
        ax.plot(zeros.real, zeros.imag, "o", markersize=9, markerfacecolor="none",
                color="tab:blue", label="Zeros")
        ax.plot(poles.real, poles.imag, "x", markersize=10, color="tab:red", label="Poles")
        ax.axhline(0, color="gray", linewidth=0.5)
        ax.axvline(0, color="gray", linewidth=0.5)
        ax.set_aspect("equal")
        ax.set_xlabel("Real part")
        ax.set_ylabel("Imaginary part")
        ax.grid(True)

    axes[0].set_title("Pole-zero plot (full view)")
    axes[0].legend(loc="upper left")

    cx, cy = zeros.real.mean(), 0.0
    span = 0.05
    axes[1].set_xlim(cx - span, cx + span)
    axes[1].set_ylim(-span, span)
    axes[1].set_title("Zoom near the zeros/poles")

    fig.suptitle(
        f"Poles |p| = {np.round(np.abs(poles), 4)}  ->  "
        f"{'STABLE' if stable else 'UNSTABLE'} (all |p| < 1)"
    )
    fig.tight_layout()
    save_fig(fig, path)
    return poles, zeros, stable

    

#main
def run():
    print("Part 4: Audio Filtering")

    input_path = config.NOISY_WAV
    if not input_path.exists():
        print(f"  Input audio not found: {input_path}")
        print("  Run Part 3 first: python main.py 3 4")
        return

    out = out_dir(4)

    #Load the noisy audio
    fs, noisy = read_wav_mono_or_stereo(input_path)
    print(f"  Input file: {input_path}")
    print(f"  Sampling rate: {fs} Hz")
    print(f"  Audio shape: {noisy.shape}")
    print(f"  Duration: {len(noisy) / fs:.2f} seconds")
    print(f"  Interference frequency: {NOTCH_FREQUENCY_HZ} Hz")

    #calculate the filter coefficients
    w0, b, a, gain = calculate_notch_coefficients(
        fs, NOTCH_FREQUENCY_HZ, POLE_RADIUS
    )
    print("\n  Second-order notch filter coefficients:")
    print(f"  w0 = {w0:.8f} rad/sample")
    print(f"  Pole radius r = {POLE_RADIUS}")
    print(f"  Normalization gain K = {gain:.8f}")
    print(f"  b (numerator)   = {b}")
    print(f"  a (denominator) = {a}")

    #filter the signal and save
    filtered = apply_notch_filter(noisy, b, a)
    filtered_new = remove_edge_clicks(filtered, fs)
    output_path = out / "filtered.wav"
    write_float_wav(output_path, fs, filtered_new)

    
    before_level = band_rms_near_frequency(noisy, fs, NOTCH_FREQUENCY_HZ)
    after_level = band_rms_near_frequency(filtered_new, fs, NOTCH_FREQUENCY_HZ)
    reduction = attenuation_db(before_level, after_level)

    print("\n  Before/after measurements:")
    print(f"  Narrow-band level before filtering: {before_level:.6g}")
    print(f"  Narrow-band level after filtering : {after_level:.6g}")
    print(f"  Reduction near {NOTCH_FREQUENCY_HZ} Hz: {reduction:.2f} dB")
    print(f"  Filtered audio saved to: {output_path}")
    
    #zero
    poles, zeros, stable = plot_pole_zero(b, a, out / "04_pole_zero_plot.png")
    print("\n  Zeros =", np.round(zeros, 6))
    print("  Poles =", np.round(poles, 6))
    print(f"  Pole magnitudes = {np.abs(poles)}  -> stable: {stable}")
    
    #save plots
    plot_waveform_comparison(
        noisy, filtered_new, fs, out / "01_waveform_comparison.png"
    )
    plot_spectrum_comparison(
        noisy, filtered_new, fs, NOTCH_FREQUENCY_HZ,
        out / "02_spectrum_comparison.png"
    )
    plot_filter_response(
        b, a, fs, NOTCH_FREQUENCY_HZ,
        out / "03_notch_frequency_response.png"
    )

    print(f"  Plots saved in: {out}")


if __name__ == "__main__":
    run()
