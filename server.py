from flask import Flask, request, send_file
from flask_cors import CORS
import pickle

app = Flask(__name__)
CORS(app)

from bark import SAMPLE_RATE, generate_audio, preload_models
from scipy.io.wavfile import write as write_wav
import numpy as np
from IPython.display import Audio
from pathlib import Path
from bark.generation import (
    generate_text_semantic,
    preload_models,
)
from bark.api import semantic_to_waveform


# download and load all models
preload_models()
GEN_TEMP = 0.6
SPEAKER = "v2/en_speaker_6"
silence = np.zeros(int(0.25 * SAMPLE_RATE))  # quarter second of silence

@app.route('/predict', methods=['POST']) 
def predict():
    content = request.get_json()
    text = content['text']

    history_prompt = SPEAKER
    if "speaker_name" in content:
        history_prompt = content['speaker_name']

    
    audio_array = generate_audio(text, history_prompt=history_prompt)
    file_name = f"text2flix_{Path(history_prompt).name}.wav"
    # save audio to disk
    write_wav(file_name, SAMPLE_RATE, audio_array)
    
    # # play text in notebook
    Audio(audio_array, rate=SAMPLE_RATE)

    return send_file(file_name, mimetype='audio/wav')

@app.route('/predict-bulk', methods=['POST']) 
def predict_bulk():
    content = request.get_json()
    text = content['text']

    history_prompt = SPEAKER
    if "speaker_name" in content:
        history_prompt = content['speaker_name']

    sentences = text.split(".?")
    pieces = []
    for sentence in sentences:
        semantic_tokens = generate_text_semantic(
            sentence,
            history_prompt=history_prompt,
            temp=GEN_TEMP,
            min_eos_p=0.05,  # this controls how likely the generation is to end
        )

        audio_array = semantic_to_waveform(semantic_tokens, history_prompt=SPEAKER,)
        pieces += [audio_array, silence.copy()]
    audio_array = np.concatenate(pieces)
    file_name = f"text2flix_{Path(history_prompt).name}.wav"
    # save audio to disk
    write_wav(file_name, SAMPLE_RATE, audio_array)

if __name__ == '__main__':
   app.run(debug=True) 