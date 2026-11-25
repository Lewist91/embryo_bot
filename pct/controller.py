import numpy as np

class PCTController:
    """4-variable Perceptual Control Theory homeostat."""

    def __init__(self):
        # Desired internal comfort setpoints (0.0 to 1.0)
        self.references = {
            "auditory_comfort": 0.35, #Prefers moderate sound, dislikes loud yelling
            "acoustic_novelty": 0.45, #Dislikes endless flat droning
            "energy": 0.80, #Virtual battery/fatigue level
            "social_warmth":0.60, #Virtual drive to interact when room is silent
        }

        # Current internal perceptions
        self.perceptions = {
            "auditory_comfort": 0.35,
            "acoustic_novelty": 0.45,
            "energy": 0.85,
            "social_warmth": 0.60
        }

    def step(self, loudness: float, novelty: float, spoke:bool = False) -> dict:
        #1. Update live auditory perceptions
        self.perceptions["auditory_comfort"] = float(np.clip(loudness, 0.0, 1.0))
        self.perceptions["acoustic_novelty"] = float(np.clip(novelty, 0.0, 1.0))

        #2. Update virtual homeostatic variables
        energy_cost = 0.03 if spoke else 0.01
        self.perceptions["energy"] = float(np.clip(self.perceptions["energy"] - energy_cost, 0.0, 1.0))

        # Gentle room sound boosts warmth; dead silence slowly drains it
        if 0.15 <= loudness <= 0.65:
            warmth_delta = 0.02
        else:
            warmth_delta = -0.015
        
        self.perceptions["social_warmth"] = float(
            np.clip(self.perceptions["social_warmth"] + warmth_delta, 0.0, 1.0)
        )

        #3. Compute PCT error signals (Reference - Perception)
        errors = {
            key: round(self.references[key] - self.perceptions[key], 3)
            for key in self.references
        }

        #4. Calculate total homeostatic distress (dum of absolute errors)
        total_distress = round(sum(abs(e) for e in errors.values()), 3)

        return{
            "perceptions": self.perceptions.copy(),
            "errors": errors,
            "total_distress": total_distress,
        }

if __name__ == "__main__":
    pct = PCTController()

    print("--- Scenario 1: Endless boring drone (low novelty) ---")
    print(pct.step(loudness=0.35, novelty=0.02, spoke=True))

    print("\n--- Scenario 2: User yells 'SHUT UP!' (huge loudness spike) ---")
    print(pct.step(loudness=0.95, novelty=0.80, spoke=False))