import numpy as np
import sounddevice as sd

class EmbryoSynth:
    """Real-time NumPy sine-wave oscillator driven by PCT error signals."""

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        
    def vocalize(
            self, 
            pitch: float = 0.5,
            glide: float = 0.5,
            grit: float = 0.2,
            pulse: float = 0.0,
            duration: float = 0.35,
    ):
        #1. Keep all motor dials safely inside 0.0 to 1.0
        pitch = float(np.clip(pitch, 0.0, 1.0))
        glide = float(np.clip(glide, 0.0, 1.0))
        grit = float(np.clip(grit, 0.0, 1.0))
        pulse = float(np.clip(pulse, 0.0,1.0))

        #2 Build a timeline of audio samples
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)

        #3. Map pitch (150 Hz -> 850 Hz) + upward/downward chirp glide
        start_freq = 150.0 + (pitch * 700.0)
        end_freq = start_freq * (0.5 + glide) # <0.5 drops pitch, >0.5 rises
        instant_freq = np.linspace(start_freq, end_freq, len(t))
        phase = 2.0 * np.pi * np.cumsum(instant_freq) / self.sample_rate

        #4. Add FM "grot" (makes a pure flute tone sound buzzy/robotic)
        modulator = np.sin(phase * 2.0) * (grit * 3.0)
        wave = np.sin(phase + modulator)

        #5. Add rhythmic stutter/pulse (0 = smooth, 1 = fast trill)
        if pulse > 0.5:
            lfo_rate = 4.0 + (pulse * 22.0)
            wave = wave * (0.5 + 0.5 * np.sin(2.0 * np.pi * lfo_rate * t))

        #6. Fade the start and end slightly so speakers don't click
        fade_len = min(int(self.sample_rate * 0.015), len(wave) // 4)
        envelope = np.ones_like(wave)
        envelope[:fade_len] = np.linspace(0.0, 1.0, fade_len)
        envelope[-fade_len:] = np.linspace(1.00, 0.0, fade_len)

        audio = (wave * envelope * 0.25).astype(np.float32)
        sd.play(audio,  self.sample_rate)
        sd.wait()
        
if __name__=="__main__":
    synth = EmbryoSynth()
    rng = np.random.default_rng()

    print("Babbling 6 random vocalizations...")
    for i in range(6):
                   p, g, r, u = rng.uniform(0.0, 1.0, size=4)
                   print(f"Babble {i + 1}: pitch={p:.2f}, glide={g:.2f}, grit={r:.2f}, pulse={u:.2f}")
                   synth.vocalize(pitch=p, glide=g, grit=r, pulse=u)
    print("Done!")