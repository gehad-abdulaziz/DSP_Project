# Multi-Domain Digital Signal Processing – Project Report

Team report · Digital Signal Processing course · November 2026

## Part 1 – Mathematical Signal & DTFT

### Objective

Generate a discrete-time signal made of two sinusoids plus Gaussian noise, compute its DTFT directly from the defining equation using loops, and plot the magnitude and phase spectra.

### Method

- Sampling frequency fs = 1000 Hz and N = 64 samples.
- Two sinusoids at 100 Hz (amplitude 1.0) and 250 Hz (amplitude 0.6), plus Gaussian noise with standard deviation 0.3. A fixed random seed makes the results repeatable.
- The DTFT is computed from the definition X(ω) = Σ x\[n\]·e^(−jωn) using two nested loops: one over 512 frequency points between −π and π, and one over the 64 samples.
- Magnitude and phase are plotted against the normalized frequency ω/π.
- Two extra checks: a comparison with np.fft, and a study of how the number of samples N changes the spectrum.

### Results

**Figure 1** – The clean and noisy signals in the time domain. *(insert outputs/part1/01\_time\_signal.png)*

**Figure 2** – DTFT magnitude and phase of the noisy signal. *(insert outputs/part1/02\_dtft\_magnitude\_phase.png)*

**Figure 3** – Effect of the number of samples N. *(insert outputs/part1/03\_effect\_of\_N.png)*

Observations:

- The magnitude has four peaks at ω/π = ±0.2 and ±0.5. Using f = ω·fs/(2π), these correspond to 100 Hz and 250 Hz, the two sinusoids we added. The peaks detected from the spectrum were about 99 Hz and 251 Hz; the 1–2 Hz difference comes from the finite frequency grid.
- The peak of the 100 Hz sinusoid is higher than the 250 Hz one because its amplitude is larger (1.0 versus 0.6).
- The magnitude is symmetric around ω = 0 because the signal is real.
- The phase looks random away from the peaks. There the magnitude is small and the noise dominates, so the phase is only meaningful near the peaks.
- The maximum difference between our loop-based DTFT and np.fft was about 3×10⁻¹³, so the manual implementation is correct. The FFT is simply the DTFT sampled at ω = 2πk/N.
- With more samples N, the peaks become narrower, which means better frequency resolution.

### Theory

**Discrete-time signals.** A discrete-time signal x\[n\] is defined only at integer values of n. It usually comes from sampling a continuous signal every Ts = 1/fs seconds, so x\[n\] = x(nTs).

**Angular frequency.** In discrete time we use the angular frequency ω in radians per sample: ω = 2πf/fs. For example, a 100 Hz sinusoid sampled at 1000 Hz has ω = 0.2π. Because e^(jωn) repeats when ω changes by 2π, the DTFT is periodic with period 2π, so one period (−π to π) is enough. The value ω = π corresponds to fs/2, the Nyquist frequency, which is the highest frequency that can be represented.

**DTFT.** The discrete-time Fourier transform is X(ω) = Σ x\[n\]·e^(−jωn). It shows how much of each frequency ω is present in the signal. It is a continuous function of ω even though x\[n\] is discrete, and it is generally complex. For a finite signal of N samples the sum runs from n = 0 to N − 1.

**Magnitude and phase.** Since X(ω) is complex, we write it as X(ω) = |X(ω)|·e^(j∠X(ω)). The magnitude |X(ω)| shows the strength of each frequency, so the sinusoids appear as peaks. The phase ∠X(ω) shows the time shift of each frequency component. For a real signal the magnitude is even and the phase is odd.

## Part 2 – Convolution & Difference Equations

### Objective

Filter a noisy signal with a moving average using linear convolution, compare time-domain convolution with frequency-domain multiplication (using zero-padding), and implement a first-order difference equation.

### Method

- Test signal: a 20 Hz sinusoid sampled at fs = 1000 Hz with N = 200 samples, plus Gaussian noise with standard deviation 0.5. A fixed random seed makes the results repeatable.
- Moving average: an M-point filter with impulse response h\[n\] = 1/M for n = 0 ... M−1, applied with np.convolve for M = 3, 5 and 11.
- Frequency domain: x and h are both zero-padded to L = N + M − 1, transformed with the FFT, multiplied, and transformed back. The result is compared with np.convolve. A second run with L = N (no extra padding) shows what goes wrong without it.
- Frequency response: |H(ω)| of each moving average is computed from the zero-padded FFT of its impulse response.
- Difference equation: y\[n\] = a·y\[n−1\] + x\[n\] is computed with a loop for a = 0.8 and a = 1.2 using a unit impulse as input, and verified against scipy.signal.lfilter.

### Results

**Figure 4** – Moving average output for M = 3, 5 and 11. *(insert report/figures/part2/01\_moving\_average.png)*

**Figure 5** – Time-domain versus frequency-domain convolution, and the effect of missing zero-padding. *(insert report/figures/part2/02\_time\_vs\_frequency.png)*

**Figure 6** – Frequency response of the moving average for M = 3, 5 and 11. *(insert report/figures/part2/03\_frequency\_response.png)*

**Figure 7** – Impulse response of the difference equation for a = 0.8 and a = 1.2. *(insert report/figures/part2/04\_difference\_equation.png)*

Observations:

- The output length is N + M − 1 (202, 204 and 210 samples for M = 3, 5 and 11), as expected from linear convolution.
- A larger M removes more noise and gives a smoother output, but it also smooths the signal itself. The edges are affected because the signal is treated as zero outside its limits.
- With zero-padding the time-domain and frequency-domain results agree to about 4.4×10⁻¹⁶, which is floating point rounding only.
- Without zero-padding the maximum error is about 0.237, and it appears only in the first M − 1 = 4 samples. The DFT product is a circular convolution, so the tail of the linear result wraps around to the beginning.
- The moving average is a low-pass filter. Its magnitude is |sin(Mω/2) / (M·sin(ω/2))|, with nulls at ω = 2πk/M. For M = 3 the null is at ω/π ≈ 0.667, for M = 5 at 0.4 and 0.8, and for M = 11 at multiples of 2/11 ≈ 0.182.
- A larger M gives a narrower main lobe, so the cutoff moves to lower frequencies and more noise is removed.
- For a = 0.8 the output decays as 0.8ⁿ and reaches about 1.7×10⁻⁴ at n = 39. For a = 1.2 it grows as 1.2ⁿ and reaches about 1.2×10³ at n = 39.
- The loop implementation matches scipy.signal.lfilter with zero difference.

### Theory

**Impulse response and LTI systems.** A discrete-time system is linear if it obeys superposition, and time-invariant if delaying the input delays the output by the same amount. A system with both properties is called LTI. The impulse response h\[n\] is the output when the input is the unit impulse δ\[n\], and it describes an LTI system completely.

**Convolution.** For an LTI system the output for any input is y\[n\] = Σ x\[k\]·h\[n−k\]. If x has N samples and h has M samples, y has N + M − 1 samples. Convolution in time corresponds to multiplication in frequency, Y(ω) = X(ω)·H(ω). With the DFT this product gives a circular convolution, so both sequences must be zero-padded to at least N + M − 1 samples to obtain the linear result.

**Difference equations.** An LTI system can also be described by a difference equation. The first-order equation used here is y\[n\] = a·y\[n−1\] + x\[n\]. Its transfer function is H(z) = 1 / (1 − a·z⁻¹), with one pole at z = a, and its impulse response is h\[n\] = aⁿ for n ≥ 0. The response has infinite length, so the system is IIR, while the moving average stops after M samples and is FIR. The system is stable only when |a| < 1, because then the pole lies inside the unit circle and the sum of |h\[n\]| is finite. For |a| = 1 the response neither decays nor grows (marginal case), and for |a| > 1 it grows without bound.

## Part 3 – Audio Analysis

*To be written by Student 3.*

## Part 4 – Audio Filtering

*To be written by Student 4.*

## Part 5 – 2D Fourier & Image Filtering

*To be written by Student 5.*

## Part 6 – Image Denoising & Evaluation

*To be written by Student 6.*
