import numpy as np
import sounddevice as sd

class AudioEncoder:
    """Captures microphone chunks and extracts loudness, novelty, and spike-ready bands."""

    def __init__(self, sample_rate: int = 44100, chunk_duration: float = 0.25, n_bands: int = 16):
        self.sample_rate = sample_rate
        self.chunk_samples = int(sample_rate * chunk_duration)
        self.n_bands = n_bands
        self.prev_bands = np.zeros(n_bands, dtype=np.float32)

    def listen_chunk(self) -> dict:
        #1. Record a short slice of audio from the default Windows microphone
        recording = sd.rec(
            self.chunk_samples,
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32",
        )
        sd.wait()
        samples = recording.flatten()

        #2. Measure overall loudness (RMS energy scaled to 0.0 -> 1.0)
        rms = float(np.sqrt(np.mean(samples ** 2)))
        loudness = float(np.clip(rms * 8.0, 0.0, 1.0))

        #3. Convert audio wave into frequency spectrum via FFT
        spectrum = np.abs(np.fft.rfft(samples))
        useful_bins = spectrum[:len(spectrum) // 2] #Focus on vocal/room frequencies
        splits = np.array_split(useful_bins, self.n_bands)
        raw_bands = np.array([float(np.mean(b)) for b in splits], dtype=np.float32)

        # Normalize bands between 0.0 and 1.0
        max_val = float(np.max(raw_bands))
        bands = raw_bands / max_val if max_val > 1e-6 else raw_bands

        #4. Measure acoustic novelty (how different this chunkj is from the last chunk)
        diff = float(np.mean(np.abs(bands - self.prev_bands)))
        novelty = float(np.clip(diff * 3.0, 0.0, 1.0))
        self.prev_bands = bands

        #5. Convert bands into binary spikes (1 or 0) ready for Akida later
        spikes = (bands > 0.45).astype(np.uint8)

        return {
                "loudness": loudness,
                "novelty": novelty,
                "bands": bands,
                "spikes": spikes
        }

if __name__ == "__main__":
    ears = AudioEncoder()
    print("Listening to your room for 6 chunks (try clapping, humming, or staying quiet)...")
    for i in range(6):
       percepts = ears.listen_chunk()
       print(
           f"Chunk {i + 1}: loudness={percepts['loudness']:.2f} | "
           f"novelty={percepts['novelty']:.2f} | "
           f"spikes={percepts['spikes'].tolist()}"
       )