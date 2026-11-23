"""Part 2 - Convolution & Difference Equations

Tasks (from the project brief):
  1. Apply a Moving Average filter using linear convolution (np.convolve).
  2. Compare time-domain convolution with frequency-domain multiplication,
     using zero-padding to obtain linear (not circular) convolution.
  3. Implement a simple first-order difference equation.

Extras: frequency response for several window lengths M, a demonstration of
what happens without zero-padding, and stable vs unstable behaviour of the
difference equation.

Key relations:
  Moving average      y[n] = (1/M) * sum_{k=0}^{M-1} x[n-k]   ->  h = ones(M)/M
  Linear convolution  length(y) = N + M - 1
  Convolution theorem y = IFFT( FFT(x, L) * FFT(h, L) ),  L >= N + M - 1
  Difference equation y[n] = a*y[n-1] + x[n]   ->  impulse response h[n] = a^n
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import lfilter

import config
from common.io_utils import out_dir
from common.plot_utils import save_fig

# ------------------------------------------------------------------
# Settings (change these to experiment)
# ------------------------------------------------------------------
FS = 1000                # sampling frequency in Hz
N = 200                  # number of samples of the test signal
F_SIGNAL = 20            # frequency of the useful sinusoid in Hz
NOISE_STD = 0.5          # standard deviation of the Gaussian noise
M_VALUES = (3, 5, 11)    # moving average window lengths
M_DEMO = 5               # window length used in the domain comparison
NUM_FREQ_POINTS = 1024   # FFT size used to evaluate the frequency response
A_STABLE = 0.8           # |a| < 1 : the output decays
A_UNSTABLE = 1.2         # |a| > 1 : the output grows without bound
NUM_Y = 40               # number of output samples of the difference equation


# ------------------------------------------------------------------
# Step 1: test signal and moving average
# ------------------------------------------------------------------
def generate_signal(num_samples):
    """Returns n, clean sinusoid, noisy sinusoid."""
    rng = np.random.default_rng(config.SEED)   # fixed seed -> same noise every run
    n = np.arange(num_samples)
    t = n / FS
    clean = np.sin(2 * np.pi * F_SIGNAL * t)
    noisy = clean + rng.normal(0, NOISE_STD, num_samples)
    return n, clean, noisy


def moving_average_kernel(M):
    """Impulse response of an M-point moving average: M equal weights summing to 1."""
    if M < 1:
        raise ValueError("Window length M must be a positive integer")
    return np.ones(M) / M


def moving_average_time(x, M):
    """Linear convolution in the time domain. Output length is len(x) + M - 1."""
    return np.convolve(x, moving_average_kernel(M), mode="full")


# ------------------------------------------------------------------
# Step 2: frequency-domain convolution
# ------------------------------------------------------------------
def convolve_freq(x, h):
    """Linear convolution through the frequency domain.

    Both sequences are zero-padded to L = N + M - 1 so that the circular
    convolution implied by the DFT equals the linear convolution.
    """
    L = len(x) + len(h) - 1
    X = np.fft.fft(x, L)      # fft(x, L) zero-pads x up to length L
    H = np.fft.fft(h, L)
    return np.real(np.fft.ifft(X * H))


def convolve_freq_no_padding(x, h):
    """Same idea but WITHOUT enough padding (length N only).

    The result is a circular convolution: the last M-1 samples of the full
    output wrap around and corrupt the first M-1 samples.
    """
    L = len(x)
    return np.real(np.fft.ifft(np.fft.fft(x, L) * np.fft.fft(h, L)))


def frequency_response(h):
    """Returns omegas in [0, pi] and H(w) of an FIR filter h (zero-padded FFT)."""
    H = np.fft.rfft(h, NUM_FREQ_POINTS)
    omegas = np.linspace(0, np.pi, len(H))
    return omegas, H


# ------------------------------------------------------------------
# Step 3: first-order difference equation
# ------------------------------------------------------------------
def difference_equation(x, a):
    """Solves y[n] = a*y[n-1] + x[n] with y[-1] = 0, using a loop."""
    y = np.zeros(len(x))
    for n in range(len(x)):
        previous = y[n - 1] if n > 0 else 0.0
        y[n] = a * previous + x[n]
    return y


# ------------------------------------------------------------------
# Plots
# ------------------------------------------------------------------
def plot_moving_average(n, noisy, clean, path):
    """Noisy signal against the moving average output for each M."""
    fig, axes = plt.subplots(len(M_VALUES), 1, figsize=(10, 9), sharex=True)
    for ax, M in zip(axes, M_VALUES):
        y = np.convolve(noisy, moving_average_kernel(M), mode="same")  # same length as x
        ax.plot(n, noisy, color="lightsteelblue", label="Noisy input")
        ax.plot(n, clean, "--", color="navy", alpha=0.6, label="Clean sinusoid")
        ax.plot(n, y, color="royalblue", linewidth=2, label=f"Moving average, M = {M}")
        ax.set_ylabel("Amplitude")
        ax.set_title(f"Moving average with M = {M}")
        ax.grid(True)
        ax.legend(loc="upper right")
    axes[-1].set_xlabel("Sample index n")
    save_fig(fig, path)


def plot_domain_comparison(x, M, path):
    """Time-domain vs frequency-domain result, and the effect of missing zero-padding."""
    h = moving_average_kernel(M)
    y_time = np.convolve(x, h, mode="full")
    y_freq = convolve_freq(x, h)
    y_circ = convolve_freq_no_padding(x, h)

    fig, (ax_top, ax_mid, ax_bot) = plt.subplots(3, 1, figsize=(10, 10))

    # Both methods overlaid
    ax_top.plot(y_time, color="navy", linewidth=3, label="Time domain (np.convolve)")
    ax_top.plot(y_freq, "--", color="deepskyblue", linewidth=1.5,
                label="Frequency domain (zero-padded)")
    ax_top.set_title(f"Linear convolution, two methods (M = {M}, length {len(y_time)})")
    ax_top.set_xlabel("Sample index n")
    ax_top.set_ylabel("Amplitude")
    ax_top.grid(True)
    ax_top.set_ylim(-1.4, 2.0)
    ax_top.legend(loc="upper left", ncol=2)

    # Error with zero-padding: only rounding noise
    ax_mid.semilogy(np.abs(y_time - y_freq) + 1e-20, color="royalblue",
                    label="|time - freq| with zero-padding")
    ax_mid.set_title("Difference between the two methods (floating point error only)")
    ax_mid.set_xlabel("Sample index n")
    ax_mid.set_ylabel("Absolute error")
    ax_mid.grid(True)
    ax_mid.legend()

    # Error without zero-padding: wrap-around in the first M-1 samples
    err_circ = np.abs(y_time[:len(x)] - y_circ)
    ax_bot.plot(err_circ, color="steelblue", label="|time - freq| without zero-padding")
    ax_bot.set_title(f"Without zero-padding the first M-1 = {M - 1} samples are corrupted")
    ax_bot.set_xlabel("Sample index n")
    ax_bot.set_ylabel("Absolute error")
    ax_bot.grid(True)
    ax_bot.legend()

    fig.tight_layout()
    save_fig(fig, path)


def plot_frequency_responses(path):
    """|H(w)| of each moving average. Nulls appear at multiples of 2*pi/M."""
    shades = ("navy", "royalblue", "deepskyblue")
    fig, ax = plt.subplots(figsize=(10, 6))
    for M, color in zip(M_VALUES, shades):
        omegas, H = frequency_response(moving_average_kernel(M))
        ax.plot(omegas / np.pi, np.abs(H), color=color, label=f"M = {M}")
    ax.set_title("Frequency response of the moving average filter")
    ax.set_xlabel(r"Normalized frequency  $\omega / \pi$  (rad/sample)")
    ax.set_ylabel(r"Magnitude  $|H(\omega)|$")
    ax.grid(True)
    ax.legend()
    save_fig(fig, path)


def plot_difference_equation(path):
    """Impulse response of y[n] = a*y[n-1] + x[n] for a stable and an unstable a."""
    impulse = np.zeros(NUM_Y)
    impulse[0] = 1.0
    n = np.arange(NUM_Y)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, a, color, label in (
        (axes[0], A_STABLE, "royalblue", "stable"),
        (axes[1], A_UNSTABLE, "navy", "unstable"),
    ):
        y = difference_equation(impulse, a)
        ax.stem(n, y, linefmt=color, markerfmt="o", basefmt="b-", label=f"Loop output, a = {a}")
        ax.plot(n, a ** n, "--", color="deepskyblue", label=r"Theory  $a^n$")
        ax.set_title(f"a = {a} ({label})")
        ax.set_xlabel("Sample index n")
        ax.set_ylabel("y[n]")
        ax.grid(True)
        ax.legend()
    fig.suptitle("Impulse response of the first-order difference equation")
    fig.tight_layout()
    save_fig(fig, path)


# ------------------------------------------------------------------
# Main entry point (called by main.py)
# ------------------------------------------------------------------
def run():
    out = out_dir(2)
    print("Part 2: Convolution & Difference Equations")

    # 1) signal and moving average
    n, clean, noisy = generate_signal(N)
    plot_moving_average(n, noisy, clean, out / "01_moving_average.png")
    for M in M_VALUES:
        y = moving_average_time(noisy, M)
        print(f"  M = {M:2d}: output length = {len(y)} (expected {N} + {M} - 1 = {N + M - 1})")

    # 2) time domain vs frequency domain
    h = moving_average_kernel(M_DEMO)
    y_time = np.convolve(noisy, h, mode="full")
    y_freq = convolve_freq(noisy, h)
    y_circ = convolve_freq_no_padding(noisy, h)
    print(f"  Max error with zero-padding    : {np.max(np.abs(y_time - y_freq)):.2e}")
    print(f"  Max error without zero-padding : {np.max(np.abs(y_time[:N] - y_circ)):.2e}")
    assert np.max(np.abs(y_time - y_freq)) < 1e-10, "zero-padded result must match np.convolve"
    assert np.max(np.abs(y_time[:N] - y_circ)) > 1e-3, "without padding the wrap-around must be visible"
    plot_domain_comparison(noisy, M_DEMO, out / "02_time_vs_frequency.png")

    # 3) frequency responses
    plot_frequency_responses(out / "03_frequency_response.png")

    # 4) difference equation, verified against scipy.signal.lfilter
    impulse = np.zeros(NUM_Y)
    impulse[0] = 1.0
    for a in (A_STABLE, A_UNSTABLE):
        y_loop = difference_equation(impulse, a)
        y_scipy = lfilter([1.0], [1.0, -a], impulse)
        print(f"  a = {a}: max difference from lfilter = {np.max(np.abs(y_loop - y_scipy)):.2e}, "
              f"last sample y[{NUM_Y - 1}] = {y_loop[-1]:.3g}")
    plot_difference_equation(out / "04_difference_equation.png")

    print(f"  Plots saved in: {out}")


if __name__ == "__main__":
    run()
