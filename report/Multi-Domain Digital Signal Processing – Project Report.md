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

*To be written by Student 2.*

## Part 3 – Audio Analysis

*To be written by Student 3.*

## Part 4 – Audio Filtering

*To be written by Student 4.*

## Part 5 – 2D Fourier & Image Filtering

*To be written by Student 5.*

## Part 6 – Image Denoising & Evaluation

*To be written by Student 6.*
