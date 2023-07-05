import os
import requests
import io
import base64
from PIL import Image, PngImagePlugin
import librosa
import nltk
import math
from PIL import Image
import numpy as np
import rembg

from bark import generate_audio, SAMPLE_RATE
from scipy.io.wavfile import write as write_wav
import moviepy.editor as mp
from moviepy.editor import ImageClip, concatenate_videoclips, CompositeVideoClip, TextClip
from moviepy.audio.io.AudioFileClip import AudioFileClip

DEFAULT_WEBUI_IP = "http://127.0.0.1:7860"

def generate_img_using_sdapi(
        prompt,
        output_loc,
        idx,
        is_foreground=False
    ):
    payload = {
        "prompt": prompt,
        "steps": 50,
        "batch_size": 1,
        "cfg_scale": 7.5,
        "sampler_index": "DDIM",
        "width": 1280,
        "height": 720
    }

    response = requests.post(url=f"{DEFAULT_WEBUI_IP}/sdapi/v1/txt2img", json=payload)

    r = response.json()
    img = r.get("images")[0]
    image = Image.open(io.BytesIO(base64.b64decode(img.split(",", 1)[0])))

    png_payload = {"image": "data:image/png;base64," + img}
    response2 = requests.post(
        url=f"{DEFAULT_WEBUI_IP}/sdapi/v1/png-info", json=png_payload
    )

    pnginfo = PngImagePlugin.PngInfo()
    pnginfo.add_text("parameters", response2.json().get("info"))
    image_path = os.path.join(output_loc, str(idx) + ".png")
    if is_foreground:
        image = rembg.remove(image)
    image.save(image_path, pnginfo=pnginfo)

    return image_path

def generate_audio_from_text(text, history_prompt, file_save_path="default"):
    sentences = nltk.sent_tokenize(text)
    pieces = []
    joined_sentence = ""
    for sentence in sentences:
        if len(joined_sentence) + len(sentence) < 200:
            joined_sentence += sentence
            continue
        else:
            joined_sentence += sentence
            audio_array = generate_audio(joined_sentence, history_prompt=history_prompt)
            joined_sentence = ""           
        
        pieces += [audio_array]
    if joined_sentence != '':
        audio_array = generate_audio(joined_sentence, history_prompt=history_prompt)
        pieces += [audio_array]
    audio_array = np.concatenate(pieces)
    file_name = f"{file_save_path}.wav"
    # save audio to disk
    write_wav(file_name, SAMPLE_RATE, audio_array)
    return file_name

def generate_scene_images_and_audio(content, movie_obj, db):
    stitch_data = []
    for scene in movie_obj.scenes:
        scene_description = scene.scene_description
        foreground_image_prompt = scene.foreground_image_prompt
        foreground_image_path = generate_img_using_sdapi(foreground_image_prompt, "images",f"{scene.id}_foreground", is_foreground=True)
        scene.foreground_image_url = foreground_image_path
        background_image_prompt = scene.background_image_prompt
        background_image_path = generate_img_using_sdapi(background_image_prompt, "images",f"{scene.id}_background")
        scene.background_image_url = background_image_path

        history_prompt = scene.speaker_name
        file_name = generate_audio_from_text(scene_description, history_prompt=history_prompt, file_save_path="audio/"+str(scene.id))
        scene.audio_url = file_name
        duration = librosa.get_duration(path=file_name)
        scene.duration = duration
        stitch_data.append((foreground_image_path, file_name, duration, scene_description))
    db.session.commit()
    return stitch_data

def stitch_video(stitch_data):
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
    return output_path

def zoom_in_effect(clip, zoom_ratio=0.04):
    def effect(get_frame, t):
        img = Image.fromarray(get_frame(t))
        base_size = img.size

        new_size = [
            math.ceil(img.size[0] * (1 + (zoom_ratio * t))),
            math.ceil(img.size[1] * (1 + (zoom_ratio * t)))
        ]

        # The new dimensions must be even.
        new_size[0] = new_size[0] + (new_size[0] % 2)
        new_size[1] = new_size[1] + (new_size[1] % 2)

        img = img.resize(new_size, Image.LANCZOS)

        x = math.ceil((new_size[0] - base_size[0]) / 2)
        y = math.ceil((new_size[1] - base_size[1]) / 2)

        img = img.crop([
            x, y, new_size[0] - x, new_size[1] - y
        ]).resize(base_size, Image.LANCZOS)

        result = np.array(img)
        img.close()

        return result

    return clip.fl(effect)