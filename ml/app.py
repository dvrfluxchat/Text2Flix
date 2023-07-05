from flask import Flask, request, send_file, send_from_directory
from flask_cors import CORS
import pickle
import json



from bark import SAMPLE_RATE, preload_models
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
from flask import request, jsonify
from flask_migrate import Migrate

import os
import librosa

from moviepy.video import fx
from helper import generate_img_using_sdapi, generate_scene_images_and_audio
from db_models import db, Movie, Scene

GEN_TEMP = 0.6
SPEAKER = "v2/en_speaker_6"
silence = np.zeros(int(0.25 * SAMPLE_RATE))  # quarter second of silence
DATABASE_URL="postgresql://text2flix_user:hello123@127.0.0.1:5432/text2flix"
app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app, db)

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

@app.route('/lexica-video', methods=['POST']) 
def get_lexica_video():
    send_file("lexica_video.mp4", mimetype='video/mp4')








@app.route('/predict-script', methods=['POST']) 
def predict_script():
    return {"message": "success"}
    # os.makedirs("images", exist_ok=True)
    # os.makedirs("audio", exist_ok=True)
    # content = request.get_json()
    # print(content)
    # stitch_data = []

    # for idx, scene in enumerate(content["scenes"]):
    #     scene_description = scene["scene_description"]
    #     if "image_prompt" in scene:
    #         image_prompt = scene["image_prompt"]
    #         image_path = generate_img_using_sdapi(image_prompt, "images", idx)
    #     elif "image_url" in scene:
    #         image_url = scene["image_url"]
    #         image_path = f"images/{idx}.jpg"
    #         r = requests.get(image_url, allow_redirects=True)
    #         open(image_path, "wb").write(r.content)
    #     else:
    #         print("Image url or prompt not present in scene json")
    #         pass
    #     history_prompt = scene['speaker_name']
    #     file_name = generate_audio_from_text(scene_description, history_prompt=history_prompt, file_save_path="audio/"+str(idx))
    #     duration = librosa.get_duration(path=file_name)
    #     stitch_data.append((image_path, file_name, duration, scene_description))

    print(stitch_data)
    # stitch_data = [('images/2.jpg', 'audio/0.wav', 8.186666666666667), ('images/1.jpg', 'audio/1.wav', 10.64)]
    size = (1024, 1024)
    video_clips = []
    for idx, data in enumerate(stitch_data):
        image_path, file_name, duration, scene_description = data
        image_clip = ImageClip(image_path, duration=duration)  # Adjust the duration as needed
        audio_clip = AudioFileClip(file_name)
        txt = TextClip( f"{scene_description}\n\n", fontsize=30, color='black', method="caption", size=size, stroke_color="black", stroke_width=1, align="South")

        # Set the text clip duration the same as the image clip
        txt.duration = image_clip.duration  
        # txt = txt.set_pos("bottom")
        # Position the text clip on the image clip 
        video_clip = CompositeVideoClip([image_clip, txt])
        video_clip.duration = image_clip.duration
        video_clip = zoom_in_effect(video_clip, 0.01)

        video_clip = video_clip.set_audio(audio_clip)
        video_clips.append(video_clip)

    final_clip = concatenate_videoclips(video_clips)
    output_path = "output.mp4"  # Change the file extension as per your needs   
    final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac",fps=24)
    return send_file(output_path, mimetype='video/mp4')



@app.route('/movie', methods=['POST'])
def create_movie():
    # download and load all models
    preload_models()

    data = request.get_json()

    new_movie = Movie(title=data['title'])
    db.session.add(new_movie)
    db.session.flush()

    for scene_data in data['scenes']:
        new_scene = Scene(
            movie_id=new_movie.id,
            scene_description=scene_data['scene_description'],
            speaker_name=scene_data['speaker_name'],
            foreground_image_prompt=scene_data['foreground_image_prompt'],
            background_image_prompt=scene_data['background_image_prompt']
        )
        db.session.add(new_scene)
    db.session.commit()
    generate_scene_images_and_audio(data, new_movie, db)
    
    scenes = []
    for scene in new_movie.scenes:
        scenes.append({
            'id': scene.id,
            'scene_description': scene.scene_description,
            'speaker_name': scene.speaker_name,
            'foreground_image_prompt': scene.foreground_image_prompt,
            'background_image_prompt': scene.background_image_prompt,
            'foreground_image_url': scene.foreground_image_url,
            'background_image_url': scene.background_image_url,
            'audio_url': scene.audio_url,
            'duration': scene.duration,
            'created_at': scene.created_at.isoformat(),
            'audio_timestamp': json.loads(scene.audio_timestamps)
        })

    return jsonify({
        'id': new_movie.id,
        'title': new_movie.title,
        'scenes': scenes
    })




@app.route('/movies/<int:movie_id>', methods=['GET'])
def get_movie(movie_id):
    movie = Movie.query.get(movie_id)
    if not movie:
        return {'message': 'Movie not found'}, 404

    scenes = []
    for scene in movie.scenes:
        scenes.append({
            'id': scene.id,
            'scene_description': scene.scene_description,
            'speaker_name': scene.speaker_name,
            'foreground_image_prompt': scene.foreground_image_prompt,
            'background_image_prompt': scene.background_image_prompt,
            'foreground_image_url': scene.foreground_image_url,
            'background_image_url': scene.background_image_url,
            'audio_url': scene.audio_url,
            'duration': scene.duration,
            'created_at': scene.created_at.isoformat(),
            'audio_timestamp': json.loads(scene.audio_timestamps)
        })

    return jsonify({
        'id': movie.id,
        'title': movie.title,
        'scenes': scenes
    })


@app.route('/audio/<path:filename>')
def serve_audio(filename):
    return send_from_directory("audio/", filename)

@app.route('/images/<path:filename>')
def serve_images(filename):
    return send_from_directory("images/", filename)

# app = create_app()
# app = Flask(__name__)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)