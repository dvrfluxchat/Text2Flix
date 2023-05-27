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
import nltk
import requests
import os
import librosa
from moviepy.editor import ImageClip, concatenate_videoclips, CompositeVideoClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video import fx

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

    file_name = generate_audio_from_text(text, history_prompt=history_prompt)
    return send_file(file_name, mimetype='audio/wav')

def generate_audio_from_text(text, history_prompt, file_save_path="default"):
    sentences = nltk.sent_tokenize(text)
    pieces = []
    for sentence in sentences:
        audio_array = generate_audio(sentence, history_prompt=history_prompt)
        pieces += [audio_array]
    audio_array = np.concatenate(pieces)
    file_name = f"{file_save_path}.wav"
    # save audio to disk
    write_wav(file_name, SAMPLE_RATE, audio_array)
    return file_name


@app.route('/predict-script', methods=['POST']) 
def predict_script():
    os.makedirs("images", exist_ok=True)
    os.makedirs("audio", exist_ok=True)
    content = request.get_json()

    stitch_data = []

    for idx, scene in enumerate(content["scenes"]):
        scene_description = scene["scene_description"]
        image_url = scene["image_url"]
        image_path = f"images/{idx}.jpg"
        history_prompt = scene['speaker_name']
        r = requests.get(image_url, allow_redirects=True)
        open(image_path, "wb").write(r.content)
        file_name = generate_audio_from_text(scene_description, history_prompt=history_prompt, file_save_path="audio/"+str(idx))
        duration = librosa.get_duration(path=file_name)
        stitch_data.append((image_path, file_name, duration))

    print(stitch_data)
    # stitch_data = [('images/2.jpg', 'audio/0.wav', 8.186666666666667), ('images/1.jpg', 'audio/1.wav', 10.64)]

    video_clips = []
    for idx, data in enumerate(stitch_data):
        image_path, file_name, duration = data
        image_clip = ImageClip(image_path, duration=duration)  # Adjust the duration as needed
        audio_clip = AudioFileClip(file_name)

        video_clip = image_clip.set_audio(audio_clip)
        video_clips.append(video_clip)

    final_clip = concatenate_videoclips(video_clips, method="compose")
    output_path = "output.mp4"  # Change the file extension as per your needs   
    final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac",fps=24)
    return send_file(output_path, mimetype='video/mp4')

if __name__ == '__main__':
   app.run(debug=True) 