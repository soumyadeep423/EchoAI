from flask import Flask, request, send_file, jsonify
from transformers import AutoProcessor, BarkModel
import scipy
import os
import numpy as np

app = Flask(__name__)

processor = AutoProcessor.from_pretrained("suno/bark")
model = BarkModel.from_pretrained("suno/bark")
voice_preset = "v2/en_speaker_6"

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        text = data.get('text', '')

        inputs = processor(text, voice_preset=voice_preset)
        audio_array = model.generate(**inputs).cpu().numpy().squeeze()
        sample_rate = model.generation_config.sample_rate

        output_path = "output.wav"
        scipy.io.wavfile.write(output_path, rate=sample_rate, data=audio_array)

        return send_file(output_path, mimetype="audio/wav")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
