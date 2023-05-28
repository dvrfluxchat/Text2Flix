from flask import Flask, request, jsonify
from usellm import Message, Options, UseLLM
import requests
import json
import time
import random
import string
import os
import os
import requests
from flask import jsonify
import multiprocessing

app = Flask(__name__)
service = UseLLM(service_url="https://usellm.org/api/llm")
received_messages = {}
access_token = os.getenv('TOKEN_KEY')
dev_environment = os.getenv('DEV_ENV')

sample_url = "https://firebasestorage.googleapis.com/v0/b/fluxchathq.appspot.com/o/business%2FuGB2TqCXmPm80liNJWj1%2Fincoming%2Ff06b0d591f9e5898e9ec92e775818213.mp4?generation=1685074476278323&alt=media&token=2e24bb91-b2b4-41d0-a8e2-259d46c2dde9"


def send_video(video_url, caption):
    url = "https://graph.facebook.com/v16.0/100233876104846/messages"

    payload = json.dumps({
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": "918328414331",
        "type": "video",
        "video": {
            "link": f"{video_url}",
            "caption": f"{caption}"
        }
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    print(access_token, " ACCESSSS************************", video_url)

    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)


def run_llm(text):
    # Prepare the conversation
    messages = [
        Message(role="system", content=f"""Generate a short story about {text} for children with emphasis on words with CAPS . 
        Use [laughs] for laughter,  ... for pauses, and [clears throat] for effect. 
        Break it down into scenes, and give one image prompt per scene for Dall-E 2. 
        The Dall-E prompt should describe the scene and also add these to the prompt "digital art,photorealistic style". 
        Do not use ambiguous character names like rose and lily. 
        Please give the output in JSON format. 
        The JSON should be like this {{"scenes":[{{
            "image_prompt": "dalle image prompt",
            "story_text": "scene text"
        }}]}}
        Make sure the story_text does not exceed 3 sentences."""),
    ]

    options = Options(messages=messages)

    # Interact with the service
    scenes_and_prompts = service.chat(options)

    scenes = scenes_and_prompts['scenes']

    def generate_image(scene):
        prompt = scene['image_prompt']
        print("image - promt",prompt)
        prompt_response = service.generate_image(prompt=prompt, size='1024x1024')
        image_url = prompt_response[0]

        scene_image = {
            'image_url': image_url,
            'speaker_name': 'v2/en_speaker_9',
            'scene_description': scene['story_text']
        }
        return scene_image

    processes = []
    for scene in scenes:
        p = multiprocessing.Process(target=generate_image, args=(scene,))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    for scene in scenes:
        scene_image = generate_image(scene)
        scenes_and_prompts.append(scene_image)

    # Print the assistant's response
    print(scenes_and_prompts.content)


@app.route('/', methods=['GET'])
def get_request():
    return 'Hello, World!'


@app.route('/whatsapp/webhook', methods=['GET'])
def get_request_webhook():
    name = request.args.get('hub.challenge')
    return name


@app.route('/whatsapp/webhook', methods=['POST'])
def post_request():
    data = request.get_json()

    if 'statuses' in data['entry'][0]['changes'][0]['value']:
        response = {'message': 'Message already received'}
        return jsonify(response)

    message_id = data['entry'][0]['changes'][0]['value']['messages'][0]['id']

    if message_id in received_messages:
        print("this is already present")
        response = {'message': 'Message already received'}
        return jsonify(response)

    # Process the data as needed
    # ...
    print(data)
    text_body = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
    # Store message ID in the map
    received_messages[message_id] = True

    print("Text received:", text_body)
    run_llm(text_body)  # Call run_llm function with text_body
    # sendvideo(text_body)
    # video_url = save_video()
    # send_video(video_url,text_body)
    response = {'message': 'Data received successfully'}
    return jsonify(response)


@app.route('/save_video', methods=['GET'])
def save_video():
    # Call the external API and get the video response
    api_response = requests.get('https://samplelib.com/lib/preview/mp4/sample-5s.mp4')

    # Extract the video data from the API response
    video_data = api_response.content

    # Generate a unique file name for the video
    timestamp = str(int(time.time()))  # Get current timestamp as a string
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))  # Generate a random string of length 6
    file_name = f"video_{timestamp}_{random_string}.mp4"  # Example file name format: video_1622235237_h3x8bo.mp4

    # Create the 'static' directory if it doesn't exist
    static_directory = os.path.join(os.getcwd(), 'static')
    if not os.path.exists(static_directory):
        os.makedirs(static_directory)

    # Save the video data to a file on your server
    video_file_path = os.path.join(static_directory, file_name)
    with open(video_file_path, 'wb') as file:
        file.write(video_data)

    # Host the video file on your server
    if dev_environment == "development":
        server_url_base = "https://ec83-125-23-34-124.ngrok-free.app"
    else:
        server_url_base = "https://whatsapp-listener-78h6.onrender.com"

    video_url = f'{server_url_base}/static/' + file_name
    print("Video will be saved to", video_url)

    # Return the video URL as the response
    return video_url


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
