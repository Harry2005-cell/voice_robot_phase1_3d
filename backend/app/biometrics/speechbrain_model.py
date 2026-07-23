import os
import warnings

# Suppress torchaudio/speechbrain warnings on Windows
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", module="speechbrain")

import torch
import torchaudio
import numpy as np
from speechbrain.pretrained import EncoderClassifier
from scipy.spatial.distance import cosine

try:
    torchaudio.set_audio_backend("soundfile")
except Exception:
    pass

classifier = EncoderClassifier.from_hparams(
    source="speechbrain/spkrec-ecapa-voxceleb", 
    savedir="pretrained_models/spkrec-ecapa-voxceleb"
)

PROFILE_DIR = "app/biometrics/profiles/"
os.makedirs(PROFILE_DIR, exist_ok=True)
SIMILARITY_THRESHOLD = 0.75

def extract_embedding(audio_path):
    signal, fs = torchaudio.load(audio_path)
    embeddings = classifier.encode_batch(signal)
    return embeddings.squeeze().numpy()

def enroll_speaker(name: str, audio_path: str):
    try:
        embedding = extract_embedding(audio_path)
        np.save(os.path.join(PROFILE_DIR, f"{name}.npy"), embedding)
        return True
    except Exception as e:
        print(f"Enrollment Error: {e}")
        return False

def identify_speaker(audio_path: str):
    try:
        unknown_embedding = extract_embedding(audio_path)
    except Exception as e:
        print(f"Extraction Error: {e}")
        return "Unknown"

    best_match = "Unknown"
    highest_score = 0
    
    if not os.path.exists(PROFILE_DIR):
        return "Unknown"

    for file in os.listdir(PROFILE_DIR):
        if file.endswith(".npy"):
            known_embedding = np.load(os.path.join(PROFILE_DIR, file))
            similarity = 1 - cosine(unknown_embedding, known_embedding)
            
            if similarity > highest_score and similarity > SIMILARITY_THRESHOLD:
                highest_score = similarity
                best_match = file.replace(".npy", "")
                
    return best_match