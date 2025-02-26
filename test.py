import torch
import numpy as np
import librosa
import soundfile as sf
from pathlib import Path

# Import encoder, synthesizer, and vocoder
from encoder import inference as encoder
from synthesizer.inference import Synthesizer
from vocoder import inference as vocoder

# Load models
encoder.load_model(Path("models/encoder.pt"))
synthesizer = Synthesizer(Path("models/synthesizer.pt"))
vocoder.load_model(Path("models/vocoder.pt"))

# Step 1: Load and process speaker audio
speaker_wav_path = "sample_speaker.wav"  
wav, _ = librosa.load(speaker_wav_path, sr=16000)
embedding = encoder.embed_utterance(wav)
print("✅ Speaker embedding extracted.")

# Step 2: Generate mel spectrogram from text
text = "Hello, this is a test of the voice cloning system."
mel_spectrogram = synthesizer.synthesize_spectrograms([text], [embedding])[0]
print("✅ Mel spectrogram generated.")

# Step 3: Convert mel spectrogram to waveform
wav_output = vocoder.infer_waveform(mel_spectrogram)
output_wav_path = "cloned_voice.wav"
sf.write(output_wav_path, wav_output, 16000)
print(f"✅ Generated voice saved to {output_wav_path}.")
