"""Part 5 - 2D Fourier & Image Filtering

Tasks (from the project brief):
  1. Load an image and convert it to grayscale.
  2. Compute and display the 2D Fourier spectrum (fft2 + fftshift).
  3. Apply ideal circular Low-Pass and High-Pass masks and show the results.

Extras: effect of the mask radius, and ideal vs Gaussian low-pass (ringing).

Steps used for every filter:
    image --fft2--> spectrum --fftshift--> (low frequencies in the centre)
          --multiply by mask--> --ifftshift--> --ifft2--> filtered image
"""
import numpy as np
import matplotlib.pyplot as plt

import config
from common.io_utils import out_dir, load_gray_image
from common.plot_utils import save_fig


CUTOFF = 30              
RADII = (10, 30, 60)  


# ------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------
def compute_spectrum(img):
    return np.fft.fftshift(np.fft.fft2(img))


def log_magnitude(F):
    return np.log(1 + np.abs(F))


def distance_from_center(shape):
    rows, cols = shape
    y, x = np.ogrid[:rows, :cols]
    return np.sqrt((y - rows // 2) ** 2 + (x - cols // 2) ** 2)


def circular_mask(shape, radius):
    return distance_from_center(shape) <= radius


def gaussian_lowpass(shape, sigma):
    return np.exp(-(distance_from_center(shape) ** 2) / (2 * sigma ** 2))


def apply_mask(F, mask):
    filtered_spectrum = F * mask
    return np.real(np.fft.ifft2(np.fft.ifftshift(filtered_spectrum)))


def show_image(ax, img, title, fixed_range=True):
    if fixed_range:
        ax.imshow(img, cmap="gray", vmin=0, vmax=255)
    else:
        ax.imshow(img, cmap="gray")
    ax.set_title(title)
    ax.axis("off")


def plot_spectrum(img, F, path):
    fig, (ax_img, ax_spec) = plt.subplots(1, 2, figsize=(12, 6))
    show_image(ax_img, img, "Grayscale image")
    show_image(ax_spec, log_magnitude(F), "2D spectrum (log scale, centred)", fixed_range=False)
    save_fig(fig, path)


def plot_lowpass_highpass(F, lp_mask, hp_mask, lp_img, hp_img, path):
    fig, axes = plt.subplots(2, 3, figsize=(12, 8))
    rows = [("Low-pass", lp_mask, lp_img, True),
            ("High-pass", hp_mask, hp_img, False)]  
    for ax_row, (name, mask, result, fixed) in zip(axes, rows):
        show_image(ax_row[0], mask, f"{name} mask (white = keep)", fixed_range=False)
        show_image(ax_row[1], log_magnitude(F * mask), f"Spectrum after {name}", fixed_range=False)
        show_image(ax_row[2], result, f"{name} result", fixed_range=fixed)
    save_fig(fig, path)


def plot_effect_of_radius(img, F, radii, path):
    fig, axes = plt.subplots(2, len(radii), figsize=(4 * len(radii), 8))
    for col, r in enumerate(radii):
        lp_mask = circular_mask(img.shape, r)
        hp_mask = ~lp_mask
        energy = 100 * np.sum(np.abs(F * lp_mask) ** 2) / np.sum(np.abs(F) ** 2)
        show_image(axes[0, col], apply_mask(F, lp_mask),
                   f"Low-pass, radius {r}\n({energy:.1f}% of the energy kept)")
        show_image(axes[1, col], apply_mask(F, hp_mask),
                   f"High-pass, radius {r}", fixed_range=False)
    save_fig(fig, path)


def plot_ideal_vs_gaussian(img, F, path):
    ideal = apply_mask(F, circular_mask(img.shape, CUTOFF))
    gauss = apply_mask(F, gaussian_lowpass(img.shape, CUTOFF))
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    show_image(axes[0], img, "Original")
    show_image(axes[1], ideal, f"Ideal low-pass (radius {CUTOFF})\nripples near edges = ringing")
    show_image(axes[2], gauss, f"Gaussian low-pass (sigma {CUTOFF})\nsmooth, no ringing")
    save_fig(fig, path)



def run():
    print("Part 5: 2D Fourier & Image Filtering")
    if not config.IMAGE_PATH.exists():
        print(f"  Image not found: {config.IMAGE_PATH}")
        print("  Copy the provided image into data/ (see config.py) and run again.")
        return

    out = out_dir(5)

    img = load_gray_image()
    print(f"  Image size: {img.shape[1]} x {img.shape[0]} pixels")

    F = compute_spectrum(img)
    plot_spectrum(img, F, out / "01_original_and_spectrum.png")

    lp_mask = circular_mask(img.shape, CUTOFF)
    hp_mask = ~lp_mask                      
    lp_img = apply_mask(F, lp_mask)
    hp_img = apply_mask(F, hp_mask)
    plot_lowpass_highpass(F, lp_mask, hp_mask, lp_img, hp_img,
                          out / "02_lowpass_highpass.png")

    plot_effect_of_radius(img, F, RADII, out / "03_effect_of_radius.png")
    plot_ideal_vs_gaussian(img, F, out / "04_ideal_vs_gaussian.png")

    print(f"  Plots saved in: {out}")


if __name__ == "__main__":
    run()
