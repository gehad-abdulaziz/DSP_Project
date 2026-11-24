# Part 2 Math Notes

Quick reference for the oral discussion. Each formula is tied to the place where it appears in `convolution.py`.

## 1. Moving average filter

Kernel (`moving_average_kernel`), where M is the window length:

$$h[n] = \frac{1}{M}, \quad 0 \le n < M$$

Output (`moving_average_time`):

$$y[n] = x[n] * h[n] = \frac{1}{M}\sum_{k=0}^{M-1} x[n-k]$$

- A larger M gives more smoothing, but it also reduces the amplitude and distorts the signal itself.
- A smaller M preserves more detail but removes less noise.
- Magnitude response, with nulls at multiples of 2π/M:

$$|H(\omega)| = \left|\frac{\sin(M\omega/2)}{M\sin(\omega/2)}\right|, \qquad \omega_k = \frac{2\pi k}{M}$$

## 2. Convolution

Linear convolution of x (N samples) with h (M samples):

$$y[n] = \sum_{k} x[k]\,h[n-k], \qquad L = N + M - 1$$

In this project: 200 + 5 - 1 = 204 samples for M = 5.

Convolution theorem:

$$x[n] * h[n] \longleftrightarrow X[k]\cdot H[k]$$

The DFT product is a circular convolution, so it equals the linear one only when both sequences are padded to at least L samples.

## 3. Zero-padding (`convolve_freq`)

- Both arrays are padded to L = N + M - 1 = 204.
- The signal gets 4 zeros (200 to 204) and the kernel gets 199 zeros (5 to 204).
- In the code this happens automatically with `np.fft.fft(x, L)` and `np.fft.fft(h, L)`.
- Without enough padding (`convolve_freq_no_padding`, length N only), the last M - 1 samples of the full output wrap around and corrupt the first M - 1 = 4 samples.

## 4. Error measure

$$e[n] = |y_{time}[n] - y_{freq}[n]|$$

- With zero-padding the maximum error is about 4.4e-16, which is floating point rounding only.
- Without zero-padding the maximum error is about 0.237, and it appears only in the first 4 samples.

## 5. Sampling and signal frequency

- Sampling frequency fs = 1000 Hz, signal frequency F_SIGNAL = 20 Hz.
- Samples per cycle = fs / f = 1000 / 20 = 50.
- Generated signal and its normalized frequency:

$$x[n] = \sin\left(2\pi f \frac{n}{f_s}\right), \qquad \omega = \frac{2\pi f}{f_s} = 0.04\pi$$

## 6. Frequency response and FFT (`frequency_response`)

$$H[k] = \mathrm{FFT}(h[n]), \qquad y[n] = \mathrm{IFFT}(Y[k])$$

- `rfft` of an even length N returns N/2 + 1 points, so 1024 gives 513 points covering ω from 0 to π (positive frequencies only, valid because h is real).
- `NUM_FREQ_POINTS = 1024` sets the density of the plotted response.

## 7. Difference equation and stability (`difference_equation`)

$$y[n] = a\,y[n-1] + x[n], \qquad H(z) = \frac{1}{1 - a z^{-1}}$$

- The pole is at z = a.
- Impulse response for a causal system: h[n] = a^n u[n].
- BIBO stability needs the pole inside the unit circle, because the sum of |a|^n is finite only when |a| < 1.

| a | Behaviour | Stability |
|---|---|---|
| 0.8 | decays | stable |
| -0.8 | decays with alternating sign | stable |
| 1 | constant at 1 | marginal, not BIBO stable |
| 1.2 | grows without bound | unstable |

## Tip for the discussion

Do not memorize the formulas alone. Tie each one to the function, plot, or printed number where it shows up.

