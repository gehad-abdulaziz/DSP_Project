"""Part 6 - Image Denoising & Evaluation

Tasks (from the project brief):
  1. Add periodic sinusoidal noise to a grayscale image.
  2. Display the noisy image spectrum and build a Notch Mask from the KNOWN noise frequency.
  3. Apply the inverse 2D Fourier transform; compare original, noisy and restored images.
  4. Evaluate the restoration with MSE and PSNR.

Extras: effect of the notch radius, and the same experiment when the noisy image is
saved as a normal 8-bit image (rounded and clipped to 0..255).

Idea:  a sinusoid in the image  ->  only TWO bright points in the spectrum
       (at +(u0, v0) and -(u0, v0) from the centre).
       Set exactly those points to zero, go back with ifft2, and the stripes disappear.

Steps:
    noisy --fft2--> --fftshift--> * notch mask --ifftshift--> --ifft2--> restored
"""
import numpy as np
import matplotlib.pyplot as plt

import config
from common.io_utils import out_dir, load_gray_image
from common.plot_utils import save_fig

# ------------------------------------------------------------------
# Settings (change these to experiment)
# ------------------------------------------------------------------
AMPLITUDE = 50           # strength of the stripes (gray levels)
U0 = 60                  # noise frequency: cycles across the image WIDTH  (horizontal)
V0 = 40                  # noise frequency: cycles across the image HEIGHT (vertical)
NOTCH_RADIUS = 5         # radius of each notch, in frequency pixels
RADII = (0, 2, 5, 10, 20, 40)   # radii compared in the "effect of radius" figure


# ------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------
def add_periodic_noise(img, u0, v0, amplitude):
    """noise[y, x] = A * sin(2*pi*(u0*x/cols + v0*y/rows)).  Returns (noisy, noise)."""
    rows, cols = img.shape
    y, x = np.ogrid[:rows, :cols]
    noise = amplitude * np.sin(2 * np.pi * (u0 * x / cols + v0 * y / rows))
    return img + noise, noise


def compute_spectrum(img):
    """2D Fourier transform with the zero frequency moved to the centre."""
    return np.fft.fftshift(np.fft.fft2(img))


def log_magnitude(F):
    """Magnitude on a log scale, so weak components are visible too."""
    return np.log(1 + np.abs(F))


def noise_peak_positions(shape, u0, v0):
    """(row, col) of the two spectrum points created by the noise.
    After fftshift the centre (zero frequency) is at (rows//2, cols//2)."""
    rows, cols = shape
    cr, cc = rows // 2, cols // 2
    return [(cr + v0, cc + u0), (cr - v0, cc - u0)]


def notch_mask(shape, peaks, radius):
    """1 everywhere (keep), 0 inside a small circle around each noise peak (remove)."""
    y, x = np.ogrid[:shape[0], :shape[1]]
    mask = np.ones(shape, dtype=bool)
    for (pr, pc) in peaks:
        mask &= (y - pr) ** 2 + (x - pc) ** 2 > radius ** 2
    return mask


def apply_mask(F, mask):
    """Multiply the spectrum by the mask, then go back to the image."""
    return np.real(np.fft.ifft2(np.fft.ifftshift(F * mask)))


def mse(a, b):
    """Mean squared error between two images."""
    return float(np.mean((a - b) ** 2))


def psnr(a, b, peak=255.0):
    """Peak signal-to-noise ratio in dB (higher = closer to the original)."""
    m = mse(a, b)
    return float("inf") if m == 0 else 10 * np.log10(peak ** 2 / m)


def detect_strongest_peak(F, min_dist=30):
    """Sanity check: find the strongest spectrum point away from the centre.
    Returns its (du, dv) offset from the centre as (cols, rows)."""
    rows, cols = F.shape
    y, x = np.ogrid[:rows, :cols]
    far = (y - rows // 2) ** 2 + (x - cols // 2) ** 2 > min_dist ** 2
    mag = np.where(far, np.abs(F), 0)
    r, c = np.unravel_index(np.argmax(mag), mag.shape)
    return c - cols // 2, r - rows // 2


def show_image(ax, img, title, fixed_range=True):
    """fixed_range=True shows gray levels 0..255; False lets matplotlib stretch them."""
    if fixed_range:
        ax.imshow(img, cmap="gray", vmin=0, vmax=255)
    else:
        ax.imshow(img, cmap="gray")
    ax.set_title(title)
    ax.axis("off")


ZOOM = 150   # half-size (in frequency pixels) of the spectrum window shown around the centre


def centre_crop(arr, half=ZOOM):
    """Window of the spectrum around the centre (the full spectrum is too big to see the points)."""
    cr, cc = arr.shape[0] // 2, arr.shape[1] // 2
    return arr[cr - half:cr + half, cc - half:cc + half]


def mark_peaks(ax, peaks, shape, radius=8, half=ZOOM):
    """Red circle around each noise peak, in the coordinates of the centre crop."""
    cr, cc = shape[0] // 2, shape[1] // 2
    for (pr, pc) in peaks:
        ax.add_patch(plt.Circle((pc - cc + half, pr - cr + half), radius,
                                fill=False, color="red", linewidth=1.5))


# ------------------------------------------------------------------
# Figures
# ------------------------------------------------------------------
def plot_noisy_and_spectrum(img, noisy, F_noisy, peaks, path):
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    show_image(axes[0, 0], img, "Original")
    show_image(axes[0, 1], noisy, f"Noisy (sinusoid, A={AMPLITUDE}, u0={U0}, v0={V0})")
    show_image(axes[1, 0], log_magnitude(F_noisy), "Noisy spectrum (full)", fixed_range=False)
    show_image(axes[1, 1], centre_crop(log_magnitude(F_noisy)),
               "Noisy spectrum, zoom on the centre:\nthe 2 bright points (red circles) are the noise",
               fixed_range=False)
    mark_peaks(axes[1, 1], peaks, F_noisy.shape)
    save_fig(fig, path)


def plot_notch(F_noisy, mask, path):
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    show_image(axes[0], centre_crop(log_magnitude(F_noisy)), "Noisy spectrum (zoom)",
               fixed_range=False)
    show_image(axes[1], centre_crop(mask), f"Notch mask (radius {NOTCH_RADIUS}, black = removed)",
               fixed_range=False)
    show_image(axes[2], centre_crop(log_magnitude(F_noisy * mask)), "Spectrum after notch (zoom)",
               fixed_range=False)
    save_fig(fig, path)


def plot_comparison(img, noisy, restored, stats, path):
    """Original / noisy / restored, plus the remaining error (amplified x10)."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 8.5))
    show_image(axes[0, 0], img, "Original")
    show_image(axes[0, 1], noisy,
               f"Noisy: MSE = {stats['noisy'][0]:.1f}, PSNR = {stats['noisy'][1]:.2f} dB")
    show_image(axes[1, 0], restored,
               f"Restored: MSE = {stats['restored'][0]:.4f}, PSNR = {stats['restored'][1]:.2f} dB")
    show_image(axes[1, 1], 128 + 10 * (restored - img), "Remaining error (x10, gray = 0)")
    save_fig(fig, path)


def plot_zoom(img, noisy, restored, path, size=300):
    """Zoom into a small patch so the stripes and the restoration are easy to see."""
    r0, c0 = img.shape[0] // 2 - size // 2, img.shape[1] // 2 - size // 2
    sl = (slice(r0, r0 + size), slice(c0, c0 + size))
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.2))
    for ax, im, name in zip(axes, (img, noisy, restored), ("Original", "Noisy", "Restored")):
        show_image(ax, im[sl], f"{name} (zoom {size}x{size} px)")
    save_fig(fig, path)


def plot_radius_study(radii, psnr_float, psnr_8bit, psnr_noisy, path):
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(radii, psnr_float, "o-", label="noisy image kept as float")
    ax.plot(radii, psnr_8bit, "s-", label="noisy image saved as 8-bit (rounded + clipped)")
    ax.axhline(psnr_noisy, color="gray", linestyle="--", label="noisy image (before filtering)")
    ax.set_xlabel("Notch radius (frequency pixels)")
    ax.set_ylabel("PSNR (dB)")
    ax.set_title("Effect of the notch radius on restoration quality")
    ax.grid(True)
    ax.legend()
    save_fig(fig, path)


# ------------------------------------------------------------------
# Main entry point (called by main.py)
# ------------------------------------------------------------------
def run():
    print("Part 6: Image Denoising & Evaluation")
    if not config.IMAGE_PATH.exists():
        print(f"  Image not found: {config.IMAGE_PATH}")
        print("  Copy the provided image into data/ (see config.py) and run again.")
        return

    out = out_dir(6)

    # 1) grayscale image + periodic noise
    img = load_gray_image()
    noisy, _ = add_periodic_noise(img, U0, V0, AMPLITUDE)
    print(f"  Image size: {img.shape[1]} x {img.shape[0]} pixels")

    # 2) spectrum of the noisy image and the notch mask (from the KNOWN frequency)
    F_noisy = compute_spectrum(noisy)
    peaks = noise_peak_positions(img.shape, U0, V0)
    du, dv = detect_strongest_peak(F_noisy)
    print(f"  Strongest spectrum point is at offset (u, v) = ({du}, {dv}) "
          f"-> expected (+-{U0}, +-{V0})")
    mask = notch_mask(img.shape, peaks, NOTCH_RADIUS)
    plot_noisy_and_spectrum(img, noisy, F_noisy, peaks, out / "01_noisy_and_spectrum.png")
    plot_notch(F_noisy, mask, out / "02_notch_mask.png")

    # 3) inverse FFT -> restored image
    restored = apply_mask(F_noisy, mask)

    # 4) evaluation
    stats = {"noisy": (mse(img, noisy), psnr(img, noisy)),
             "restored": (mse(img, restored), psnr(img, restored))}
    print(f"  Noisy    : MSE = {stats['noisy'][0]:.2f}, PSNR = {stats['noisy'][1]:.2f} dB")
    print(f"  Restored : MSE = {stats['restored'][0]:.4f}, PSNR = {stats['restored'][1]:.2f} dB")
    plot_comparison(img, noisy, restored, stats, out / "03_original_noisy_restored.png")
    plot_zoom(img, noisy, restored, out / "04_zoom.png")

    # extra: effect of the notch radius (float noisy image vs 8-bit saved noisy image)
    noisy_8bit = np.clip(np.round(noisy), 0, 255)
    F_8bit = compute_spectrum(noisy_8bit)
    p_float, p_8bit = [], []
    for r in RADII:
        m = notch_mask(img.shape, peaks, r)
        p_float.append(psnr(img, apply_mask(F_noisy, m)))
        p_8bit.append(psnr(img, apply_mask(F_8bit, m)))
        print(f"  radius {r:>2}: PSNR float = {p_float[-1]:.2f} dB, 8-bit = {p_8bit[-1]:.2f} dB")
    plot_radius_study(RADII, p_float, p_8bit, psnr(img, noisy_8bit),
                      out / "05_effect_of_radius.png")

    print(f"  Plots saved in: {out}")


if __name__ == "__main__":
    run()
