## Part 3 – Audio Analysis

### Objective

Analyse the provided speech recording in the time and frequency domains (waveform, FFT spectrum and spectrogram), then add a 60 Hz sinusoidal interference (mains hum) at a known signal-to-interference ratio of −20 dB (the hum is 10 times stronger than the speech in amplitude) and save the result as `noisy.wav` for Part 4.

### Method

- The recording `data/speech.wav` is loaded with `scipy.io.wavfile`, converted to mono (its two channels are identical, so averaging changes nothing) and normalized to \[−1, 1\]. Its sampling rate is fs = 48 000 Hz, it has N = 73 728 samples and lasts 1.536 s.
- Time domain: the waveform is plotted against time in seconds, and its peak and RMS values are measured.
- Spectrum: the one-sided FFT magnitude is computed with `np.fft.rfft` on the whole signal after a Hann window (to reduce spectral leakage). The frequency axis is f\[k\] = k·fs/N, so the frequency resolution is fs/N ≈ 0.65 Hz. Magnitudes are shown in dB relative to the peak. Two numbers are extracted: the strongest peak above 20 Hz, and the frequency below which 95 % of the energy lies.
- Spectrogram: short-time Fourier transform with a 25 ms Hann window and a 10 ms step (`scipy.signal.spectrogram`), shown in dB with an 80 dB dynamic range. The clean spectrogram is shown up to 8 kHz.
- Interference: x_noisy\[n\] = x\[n\] + A·sin(2π·60·n/fs). The amplitude is chosen from the target SNR of −20 dB: A = √2·rms(x)/10^(SNR/20) = √2 · 0.0557 / 10^(−20/20) = 0.787. The sum has a peak of 1.246, which would clip in a WAV file, so `save_audio()` scales it by 0.803 (−1.9 dB) before saving it as 16-bit WAV in `outputs/part3/noisy.wav`. The scaling applies to the speech and the hum together, so the SNR of `noisy.wav` is still −20.00 dB. The figures in this part use the signal before this scaling.
- Extras: clean versus noisy comparison (time zoom and spectrum zoom), and a spectrogram of the noisy signal with a 10 ms and a 100 ms window.

### Results

**Figure 8** – Speech signal in the time domain. *(insert report/figures/part3/01\_waveform.png)*

**Figure 9** – Magnitude spectrum of the speech (full range and zoom on 0–1000 Hz). *(insert report/figures/part3/02\_spectrum.png)*

**Figure 10** – Spectrogram of the clean speech. *(insert report/figures/part3/03\_spectrogram.png)*

**Figure 11** – Clean versus noisy signal: time zoom and spectrum zoom around 60 Hz. *(insert report/figures/part3/04\_clean\_vs\_noisy.png)*

**Figure 12** – Effect of the spectrogram window length on the 60 Hz hum. *(insert report/figures/part3/05\_window\_length.png)*

Observations:

- The recording is a short utterance: silence until about 0.33 s, speech until about 0.91 s, then silence again. The peak amplitude is 0.487 and the RMS is 0.0557.
- The strongest spectral peak is at about 214 Hz, which is in the range of the speaker's pitch (fundamental frequency). The spectrum shows many closely spaced peaks, the harmonics of the pitch, with the strongest content between about 160 Hz and 3 kHz.
- 95 % of the energy lies below 2304 Hz, far below the Nyquist frequency fs/2 = 24 000 Hz. The spectrum has no visible content above about 15 kHz, so the recording is band-limited even though fs is 48 kHz.
- The speech has almost no energy at low frequencies: below 150 Hz the spectrum is 40 to 50 dB under its peak, and this region holds only 0.014 % of the energy. The clean spectrum at 60 Hz is at −47.4 dB relative to its peak.
- In the spectrogram, vowels appear as horizontal harmonic bands that rise and fall with the pitch and reach about 5 kHz. Short bursts of broadband energy up to about 15 kHz mark consonants. There is no energy before 0.33 s and after 0.95 s.
- After adding the interference, the level at 60 Hz rose from −47.4 dB to +34.5 dB (relative to the peak of the clean spectrum), an increase of 81.9 dB. The hum is a single narrow spike about 34 dB above the strongest speech component. This happens because the hum puts all its energy in one frequency, while the speech spreads its energy over thousands of frequency bins, so even a hum that is only 10 times stronger in amplitude towers over every individual speech component.
- Because the speech has almost no content near 60 Hz, a very narrow notch filter (Part 4) can remove the hum while damaging almost nothing of the speech.
- In the time domain the hum is now the dominant component: a large 60 Hz sine wave (amplitude 0.787, larger than the speech peak of 0.487) with the speech riding on top of it as fast wiggles. In the silent parts of `noisy.wav` only the pure sine is present. The speech can still be separated from the hum because the two occupy different frequencies.
- Window length trade-off: with a 10 ms window the frequency resolution is about 100 Hz, so the strong hum leaks into all the low-frequency bands and almost completely hides the speech below 250 Hz. With a 100 ms window the resolution is about 10 Hz and the hum stays in a narrow horizontal band around 60 Hz, so the pitch contour of the voice is clearly visible again. The cost is a worse time resolution: the start and end of the speech are blurred.
- Because the hum is so much stronger than the speech, Part 4 has to remove it almost completely: any hum left over would still be comparable to the speech.

### Theory

**Sampling and the Nyquist frequency.** Digital audio is a sequence of samples taken at rate fs. The highest frequency that can be represented without aliasing is fs/2, the Nyquist frequency. Speech carries most of its useful content below 4–8 kHz.

**Spectrum.** The FFT is the DTFT of a finite signal sampled at N equally spaced frequencies ω = 2πk/N, which in Hz gives f\[k\] = k·fs/N. The spacing fs/N is the frequency resolution of the spectrum, and a longer recording gives finer resolution. For a real signal the negative-frequency half only mirrors the positive half, so only 0 to fs/2 is shown. Multiplying the signal by a window (Hann) before the FFT lowers spectral leakage, at the cost of slightly wider peaks.

**Spectrogram.** Speech is non-stationary: its spectrum changes every few tens of milliseconds, so one FFT of the whole recording hides *when* each frequency occurs. The spectrogram applies the FFT to short, overlapping windowed frames and plots the result as time versus frequency, with colour showing power in dB. The window length sets the trade-off: a window of duration T gives a frequency resolution of about 1/T, so a longer window resolves frequencies better but locates events in time worse. For speech, 20–30 ms is the usual compromise.

**Voiced and unvoiced sounds.** Voiced sounds are produced by vibrating vocal cords. They are nearly periodic, so their spectrum has harmonics at multiples of the pitch f0, shaped by the resonances (formants) of the vocal tract. Unvoiced sounds (such as "s") come from turbulent air flow and have a noise-like, broadband spectrum with more high-frequency energy.

**Mains interference.** Power-line hum is a sinusoid at the mains frequency (50 Hz or 60 Hz depending on the country; 60 Hz is used in this project). As an additive interference its spectrum is a single line at ±60 Hz. The signal-to-interference ratio SNR = 10·log10(P_signal / P_hum) compares the powers, where a sinusoid of amplitude A has power A²/2.
