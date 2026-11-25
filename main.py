import time
import numpy as np

from brain.audio_encoder import AudioEncoder
from pct.controller import PCTController
from actuators.synth import EmbryoSynth


def run_embryo(cycles: int = 20):
    ears = AudioEncoder(chunk_duration=0.25)
    pct = PCTController()
    voice = EmbryoSynth()
    rng = np.random.default_rng()

    # Starting vocal tract dials: [pitch, glide, grit, pulse]
    dials = np.array([0.45, 0.50, 0.20, 0.10], dtype=np.float32)

    print("embryo_bot waking up... (Press Ctrl+C in terminal anytime to stop)\n")

    for step_num in range(1, cycles + 1):
        # 1. SENSE: Listen to the room for 0.25s
        percepts = ears.listen_chunk()
        loudness = percepts["loudness"]
        novelty = percepts["novelty"]

        # 2. FEEL: Feed live audio into the 4-variable PCT homeostat
        state = pct.step(loudness=loudness, novelty=novelty, spoke=False)
        errors = state["errors"]
        distress = state["total_distress"]

        print(
            f"[{step_num:02d}] Loud:{loudness:.2f} Nov:{novelty:.2f} | "
            f"Err(Comf:{errors['auditory_comfort']:+.2f}, Nov:{errors['acoustic_novelty']:+.2f}, "
            f"Warmth:{errors['social_warmth']:+.2f}) | Distress:{distress:.2f}"
        )

        # 3. REACT / LEARN:
        # Case A: Room got way too loud ("Shut up!" / clap) -> flinch, stay quiet, soften grit/pitch
        if errors["auditory_comfort"] < -0.25:
            print("   -> Startled! Quietly pulling back harshness and pitch.")
            dials[0] = np.clip(dials[0] - 0.15, 0.0, 1.0)  # Lower pitch
            dials[2] = np.clip(dials[2] - 0.20, 0.0, 1.0)  # Reduce grit
            time.sleep(0.5)
            continue

        # Case B: Bored (high novelty error) or lonely (high social_warmth error) -> babble!
        if errors["acoustic_novelty"] > 0.12 or errors["social_warmth"] > 0.05:
            # Boredom injects exploratory jitter into the 4 synth dials so it never drones
            jitter_scale = max(0.05, errors["acoustic_novelty"] * 0.6)
            dials = np.clip(dials + rng.normal(0.0, jitter_scale, size=4), 0.0, 1.0)

            print(
                f"   -> Babbling: pitch={dials[0]:.2f}, glide={dials[1]:.2f}, "
                f"grit={dials[2]:.2f}, pulse={dials[3]:.2f}"
            )
            voice.vocalize(
                pitch=float(dials[0]),
                glide=float(dials[1]),
                grit=float(dials[2]),
                pulse=float(dials[3]),
                duration=0.30,
            )
            # Log the energy spent speaking
            pct.step(loudness=loudness, novelty=novelty, spoke=True)
            # Brief pause so its own speaker echo fades before listening again
            time.sleep(0.15)


if __name__ == "__main__":
    try:
        run_embryo(cycles=20)
        print("\nembryo_bot finished its wake cycle.")
    except KeyboardInterrupt:
        print("\nembryo_bot put to sleep early.")