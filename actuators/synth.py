import numpy as np
import sounddevice as sd

class EmbryoSynth:
    """Real-time NumPy sine-wave oscillator driven by PCT error signals."""

    def __init__(self, sample_rate: int = 44100, base_freq: float = 220.0):
        self.sample_rate = sample_rate
        self.base_freq = base_freq

    def emit_error_tone(self, pct_error: float, duration: float = 0.6) -> None:
        """
        Convert a Perceptual Control Theory (PCT) error into an audio pitch.
        - Error = 0.0 -> calm baseline hum (220 Hz, A3)
        - Higher error -> higher pitch & slightly louder urgency
        """
        # Map error magnitude (0.0 to 1.0+) to pitch (220 Hz up to 660 Hz)
        clamped_error = max(0.0, min(abs(pct_error), 1.5))
        freq = self.base_freq + (clamped_error * 300.0)
        amplitude = 0.15 + (clamped_error * 0.15)

        #Generate time axis and sine wave
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)
        wave = amplitude * np.sin(2 * np.pi * freq * t)

        # Apply a quick 20ms fade-in/out so the speaker doesn't click
        fade_samples = int(self.sample_rate * 0.02)
        envelope = np.ones_like(wave)
        envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
        envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)

        sd.play(wave * envelope, self.sample_rate)
        sd.wait()

if __name__ == "__main__":
    synth = EmbryoSynth()
    print("Playing calm baseline (error = 0.0)...")
    synth.emit_error_tone(pct_error=0.0)

    print("Playing mild disturbamce (error = 0.4)...")
    synth.emit_error_tone(pct_error=0.4)

    print("Playing high PCT error (error = 1.0)...")
    synth.emit_error_tone(pct_error=1.0)
    print("Done!")