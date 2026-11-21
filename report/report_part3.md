## Part 3 – Audio Analysis

### Objective

Analyse the provided speech recording in the time and frequency domains (waveform, FFT spectrum and spectrogram), then add a 50 Hz sinusoidal interference (mains hum) at a known signal-to-interference ratio and save the result as `noisy.wav` for Part 4.

### Method

- The recording is loaded with `scipy.io.wavfile`, converted to mono and normalized to [−1, 1]. Its sampling rate is fs = **[fs] Hz**, it has **[N] samples** and lasts **[duration] s**.
- Time domain: the waveform is plotted against time in seconds.
- Spectrum: the one-sided FFT magnitude is computed with `np.fft.rfft` on the whole signal after a Hann window (to reduce spectral leakage). The frequency axis is f\[k\] = k·fs/N. Magnitudes are shown in dB relative to the peak. Two numbers are extracted: the strongest peak above 20 Hz, and the frequency below which 95 % of the energy lies.
- Spectrogram: short-time Fourier transform with a 25 ms Hann window and a 10 ms step (`scipy.signal.spectrogram`), shown in dB with an 80 dB dynamic range.
- Interference: x_noisy\[n\] = x\[n\] + A·sin(2π·50·n/fs). The amplitude is chosen from a target SNR of 10 dB: A = √2·rms(x)/10^(SNR/20) = **[A]**. The result is saved as 16-bit WAV in `outputs/part3/noisy.wav`.
- Extras: clean versus noisy comparison (time zoom and spectrum zoom), and a spectrogram of the noisy signal with a 10 ms and a 100 ms window.

### Results

**Figure 8** – Speech signal in the time domain. *(insert outputs/part3/01\_waveform.png)*

**Figure 9** – Magnitude spectrum of the speech (full range and zoom on 0–1000 Hz). *(insert outputs/part3/02\_spectrum.png)*

**Figure 10** – Spectrogram of the clean speech. *(insert outputs/part3/03\_spectrogram.png)*

**Figure 11** – Clean versus noisy signal: time zoom and spectrum zoom around 50 Hz. *(insert outputs/part3/04\_clean\_vs\_noisy.png)*

**Figure 12** – Effect of the spectrogram window length on the 50 Hz hum. *(insert outputs/part3/05\_window\_length.png)*

Observations (fill the numbers from the console output of `python main.py 3`):

- The waveform shows bursts of energy separated by low-amplitude pauses, which correspond to words and silences. Peak amplitude is **[peak]** and RMS is **[rms]**.
- The strongest spectral peak is at about **[f_dom] Hz**, in the range of the fundamental frequency (pitch) of the speaker. Pitch harmonics appear as regularly spaced peaks at multiples of this frequency.
- 95 % of the energy lies below **[f_bw] Hz**, far below the Nyquist frequency fs/2 = **[fs/2] Hz**. Most of the useful information in speech is in the low frequencies, and the spectrum falls off towards high frequencies.
- In the spectrogram, voiced sounds (vowels) show horizontal harmonic bands and dark regions mark the pauses. Dark vertical stripes of broadband energy at the highest frequencies correspond to fricative sounds such as "s" and "sh".
- After adding the interference, the level at 50 Hz rose by **[rise] dB**. In the spectrum the hum is a single narrow spike, because a pure sinusoid concentrates all its energy at one frequency. This is why a notch filter (Part 4) can remove it while damaging very little of the speech.
- In the time domain, the hum is a slow 50 Hz ripple added to the waveform. It is hard to see during loud speech but clearly visible during pauses.
- Window length trade-off: with a 10 ms window the frequency resolution is about 100 Hz, so the 50 Hz hum is smeared into the lowest band. With a 100 ms window the resolution is about 10 Hz and the hum appears as a clean horizontal line at 50 Hz. A longer window gives better frequency resolution but worse time resolution, so the spectrogram cannot have both at once.
- `save_audio()` scales the signal down only if it would clip, so the SNR of `noisy.wav` stays equal to the 10 dB target (the speech and the hum are scaled together).

### Theory

**Sampling and the Nyquist frequency.** Digital audio is a sequence of samples taken at rate fs. The highest frequency that can be represented without aliasing is fs/2, the Nyquist frequency. Speech is usually recorded at 8–16 kHz because most of its useful content lies below 4–8 kHz.

**Spectrum.** The FFT is the DTFT of a finite signal sampled at N equally spaced frequencies ω = 2πk/N, which in Hz gives f\[k\] = k·fs/N. The spacing fs/N is the frequency resolution of the spectrum, and a longer recording gives finer resolution. For a real signal the negative-frequency half only mirrors the positive half, so only 0 to fs/2 is shown. Multiplying the signal by a window (Hann) before the FFT lowers spectral leakage, at the cost of slightly wider peaks.

**Spectrogram.** Speech is non-stationary: its spectrum changes every few tens of milliseconds, so one FFT of the whole recording hides *when* each frequency occurs. The spectrogram applies the FFT to short, overlapping windowed frames and plots the result as time versus frequency, with colour showing power in dB. The window length sets the trade-off: a window of duration T gives frequency resolution of about 1/T. For speech, 20–30 ms is the usual compromise.

**Voiced and unvoiced sounds.** Voiced sounds are produced by vibrating vocal cords. They are nearly periodic, so their spectrum has harmonics at multiples of the pitch f0, shaped by the resonances (formants) of the vocal tract. Unvoiced sounds (such as "s") come from turbulent air flow and have a noise-like, broadband spectrum with more high-frequency energy.

**Mains interference.** Power-line hum is a sinusoid at the mains frequency, 50 Hz in Egypt. As an additive interference it has a spectrum made of a single line at ±50 Hz. The signal-to-interference ratio SNR = 10·log10(P_signal/P_hum) compares the powers, where a sinusoid of amplitude A has power A²/2.
