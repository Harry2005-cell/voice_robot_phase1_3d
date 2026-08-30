import os
import warnings

# Suppress torchaudio/speechbrain warnings on Windows
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", module="speechbrain")

import torch
import torchaudio
import numpy as np
from scipy.spatial.distance import cosine

try:
    from speechbrain.pretrained import EncoderClassifier
except Exception as e:
    EncoderClassifier = None
    print(f"Warning: Could not import SpeechBrain EncoderClassifier: {e}")

try:
    torchaudio.set_audio_backend("soundfile")
except Exception:
    pass

_classifier = None

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROFILE_DIR = os.path.join(CURRENT_DIR, "profiles")
os.makedirs(PROFILE_DIR, exist_ok=True)
SIMILARITY_THRESHOLD = 0.75

def get_classifier():
    global _classifier
    if EncoderClassifier is None:
        return None
    if _classifier is None:
        model_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "pretrained_models",
            "spkrec-ecapa-voxceleb"
        )
        os.makedirs(model_dir, exist_ok=True)
        try:
            _classifier = EncoderClassifier.from_hparams(
                source="speechbrain/spkrec-ecapa-voxceleb", 
                savedir=model_dir
            )
        except Exception as e:
            print(f"Warning: Could not load SpeechBrain classifier: {e}")
            return None
    return _classifier

def extract_embedding(audio_path):
    clf = get_classifier()
    if clf is None:
        return None
    signal, fs = torchaudio.load(audio_path)
    embeddings = clf.encode_batch(signal)
    return embeddings.squeeze().detach().cpu().numpy()

def enroll_speaker(name: str, audio_path: str):
    try:
        embedding = extract_embedding(audio_path)
        if embedding is None:
            return False
        os.makedirs(PROFILE_DIR, exist_ok=True)
        np.save(os.path.join(PROFILE_DIR, f"{name}.npy"), embedding)
        return True
    except Exception as e:
        print(f"Enrollment Error: {e}")
        return False

def identify_speaker(audio_path: str):
    try:
        if not os.path.exists(audio_path) or os.path.getsize(audio_path) < 1000:
            return "User", 100
        unknown_embedding = extract_embedding(audio_path)
        if unknown_embedding is None:
            return "User", 100
    except Exception as e:
        return "Unknown", 0

    best_match = "Unknown"
    highest_score = 0.0
    
    if not os.path.exists(PROFILE_DIR):
        return "Unknown", 0

    for file in os.listdir(PROFILE_DIR):
        if file.endswith(".npy"):
            known_embedding = np.load(os.path.join(PROFILE_DIR, file))
            similarity = float(1 - cosine(unknown_embedding, known_embedding))
            
            if similarity > highest_score:
                highest_score = similarity
                if similarity > SIMILARITY_THRESHOLD:
                    best_match = file.replace(".npy", "")
                
    score_percent = min(100, max(0, int(highest_score * 100)))
    return best_match, score_percent