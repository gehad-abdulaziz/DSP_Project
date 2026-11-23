# Part 1 - Mathematical Signal & DTFT

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

import config
from common.io_utils import out_dir
from common.plot_utils import save_fig

FS = 1000               
N = 64                  
F1, F2 = 100, 250       
A1, A2 = 1.0, 0.6       
NOISE_STD = 0.3         
NUM_FREQ_POINTS = 512   


def generate_signal(num_samples):
    """Returns n, clean signal, noisy signal."""
    rng = np.random.default_rng(config.SEED)   
    n = np.arange(num_samples)                 
    t = n / FS                                 
    clean = A1 * np.sin(2 * np.pi * F1 * t) + A2 * np.sin(2 * np.pi * F2 * t)
    noise = rng.normal(0, NOISE_STD, num_samples)
    return n, clean, clean + noise


def dtft_manual(x, omegas):
    """DTFT from the definition, using loops.

    x      : signal samples x[0..N-1]
    omegas : frequencies (rad/sample) where X(w) is evaluated
    """
    X = np.zeros(len(omegas), dtype=complex)
    for k in range(len(omegas)):            
        w = omegas[k]
        total = 0
        for n in range(len(x)):             
            total = total + x[n] * np.exp(-1j * w * n)
        X[k] = total
    return X


def find_two_peaks_in_hz(omegas, X):
    """Finds the two strongest peaks (for w > 0) and converts them to Hz. , magnitude tell me strong and pase tell me shift"""
    positive = omegas > 0
    w_pos = omegas[positive]
    mag_pos = np.abs(X)[positive]
    peaks, _ = find_peaks(mag_pos) 
    strongest = peaks[np.argsort(mag_pos[peaks])[-2:]] 
    return np.sort(w_pos[strongest] * FS / (2 * np.pi))   #convert from rad that in dtft to hz 

    

def plot_time_signals(n, clean, noisy, path):
    fig, ax = plt.subplots()
    ax.plot(n, clean, "o-", label="Clean (two sinusoids)")
    ax.plot(n, noisy, "s-", alpha=0.6, label="Noisy (+ Gaussian noise)")
    ax.set_title("Part 1: signal in the time domain")
    ax.set_xlabel("Sample index n")
    ax.set_ylabel("Amplitude")
    ax.grid(True)
    ax.legend()
    save_fig(fig, path)


def plot_spectrum(omegas, X, path):
    """Magnitude and phase of the DTFT."""
    x_axis = omegas / np.pi                    
    fig, (ax_mag, ax_phase) = plt.subplots(2, 1, figsize=(10, 7), sharex=True)

    ax_mag.plot(x_axis, np.abs(X))
    ax_mag.set_title("DTFT magnitude |X(w)| of the noisy signal")
    ax_mag.set_ylabel("Magnitude")

    ax_phase.plot(x_axis, np.angle(X))
    ax_phase.set_title("DTFT phase of the noisy signal")
    ax_phase.set_ylabel("Phase (rad)")
    ax_phase.set_xlabel(r"Normalized frequency  $\omega / \pi$  (rad/sample)")

    for f in (F1, F2):
        for sign in (+1, -1):
            ax_mag.axvline(sign * 2 * f / FS, color="red", linestyle="--", alpha=0.5)
    ax_mag.plot([], [], "r--", label="true frequencies") 
    ax_mag.legend()

    ax_mag.grid(True)
    ax_phase.grid(True)
    save_fig(fig, path)


def check_against_fft(x):
    """The FFT equals the DTFT sampled at w = 2*pi*k/N. Verify it."""
    k = np.arange(len(x))
    omegas = 2 * np.pi * k / len(x)
    X_loop = dtft_manual(x, omegas)
    X_fft = np.fft.fft(x)
    error = np.max(np.abs(X_loop - X_fft))
    print(f"  Max difference between manual DTFT and np.fft: {error:.2e}")


def plot_effect_of_N(path):
    """More samples -> narrower peaks (better frequency resolution)."""
    omegas = np.linspace(0, np.pi, NUM_FREQ_POINTS)
    fig, ax = plt.subplots()
    for num in (16, 32, 64):
        _, clean, _ = generate_signal(num)
        X = dtft_manual(clean, omegas)
        ax.plot(omegas / np.pi, np.abs(X) / num, label=f"N = {num}")
    ax.set_title("Effect of the number of samples N (clean signal)")
    ax.set_xlabel(r"Normalized frequency  $\omega / \pi$  (rad/sample)")
    ax.set_ylabel("Magnitude / N")
    ax.grid(True)
    ax.legend()
    save_fig(fig, path)


def run():
    out = out_dir(1)
    print("Part 1: Mathematical Signal & DTFT")

    n, clean, noisy = generate_signal(N)
    plot_time_signals(n, clean, noisy, out / "01_time_signal.png")

    omegas = np.linspace(-np.pi, np.pi, NUM_FREQ_POINTS)
    X = dtft_manual(noisy, omegas)

    plot_spectrum(omegas, X, out / "02_dtft_magnitude_phase.png")

    f_found = find_two_peaks_in_hz(omegas, X)
    print(f"  Peaks found at about {f_found[0]:.0f} Hz and {f_found[1]:.0f} Hz "
          f"(true values: {F1} and {F2} Hz)")

    check_against_fft(noisy)
    plot_effect_of_N(out / "03_effect_of_N.png")

    print(f"  Plots saved in: {out}")


if __name__ == "__main__":
    run()
