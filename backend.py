from flask import Flask, request, jsonify, send_file, render_template
import torch
import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
from encoder import inference as encoder
from synthesizer.inference import Synthesizer
from vocoder import inference as vocoder
import tempfile

app = Flask(__name__)

# Load models
encoder.load_model(Path("models/encoder.pt"))
synthesizer = Synthesizer(Path("models/synthesizer.pt"))
vocoder.load_model(Path("models/vocoder.pt"))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/voice_cloning")
def voice_cloning():
    return render_template("voicecloning.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["audio"]
    wav, _ = librosa.load(file, sr=16000)
    embedding = encoder.embed_utterance(wav)
    return jsonify({"embedding": embedding.tolist()})

@app.route("/synthesize", methods=["POST"])
def synthesize():
    data = request.json
    text = data["text"]
    embedding = np.array(data["embedding"])  # Speaker embedding
    mel_spectrogram = synthesizer.synthesize_spectrograms([text], [embedding])[0]
    return jsonify({"mel": mel_spectrogram.tolist()})

@app.route("/vocode", methods=["POST"])
def vocode():
    data = request.json
    mel = np.array(data["mel"])
    wav = vocoder.infer_waveform(mel)
    
    temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    sf.write(temp_wav.name, wav, 16000)
    return send_file(temp_wav.name, as_attachment=True, download_name="output.wav", mimetype="audio/wav")

if __name__ == "__main__":
    app.run(debug=True)