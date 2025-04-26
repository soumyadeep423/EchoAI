from flask import Flask, request, send_file, jsonify, render_template
from transformers import AutoProcessor, BarkModel
import scipy
import numpy as np
import os

app = Flask(__name__)

processor = AutoProcessor.from_pretrained("suno/bark")
model = BarkModel.from_pretrained("suno/bark")
default_voice_preset = "v2/en_speaker_6"  # fallback preset

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate")
def generate_page():
    return render_template("generate.html")

@app.route("/api/generate", methods=["POST"])
def generate_audio():
    try:
        data = request.get_json()
        text = data.get("text", "")
        voice_preset = data.get("voice_preset", default_voice_preset)

        if not text.strip():
            return jsonify({"error": "Text is required"}), 400

        inputs = processor(text, voice_preset=voice_preset)
        audio_array = model.generate(**inputs).cpu().numpy().squeeze()
        sample_rate = model.generation_config.sample_rate

        output_path = "output.wav"
        scipy.io.wavfile.write(output_path, rate=sample_rate, data=audio_array)

        return send_file(output_path, mimetype="audio/wav")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
