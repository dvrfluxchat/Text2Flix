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
import concurrent.futures


app = Flask(__name__)
service = UseLLM(service_url="https://usellm.org/api/llm")
# service = UseLLM(service_url="https://ramanafluxchathq.loca.lt/api/llm")

# https://ramanafluxchathq.loca.lt
received_messages = {}
access_token = os.getenv('TOKEN_KEY')
dev_environment = os.getenv('DEV_ENV')

sample_url = "https://firebasestorage.googleapis.com/v0/b/fluxchathq.appspot.com/o/business%2FuGB2TqCXmPm80liNJWj1%2Fincoming%2Ff06b0d591f9e5898e9ec92e775818213.mp4?generation=1685074476278323&alt=media&token=2e24bb91-b2b4-41d0-a8e2-259d46c2dde9"

def load_processed_message_ids():
    try:
        with open('processed_message_ids.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_processed_message_ids(message_ids):
    with open('processed_message_ids.json', 'w') as file:
        json.dump(message_ids, file)

def send_video(phone,video_url,caption):
    print("SENDING VIDEO MESSAGE ################ : ",video_url,caption)

    url = "https://graph.facebook.com/v16.0/100233876104846/messages"

    payload = json.dumps({
    "messaging_product": "whatsapp",
    "recipient_type": "individual",
    "to": f"{phone}",
    "type": "video",
    "video": {
        # "link": "https://ec83-125-23-34-124.ngrok-free.app/static/video_1685228995_3jigq7.mp4",
        "link": f"{video_url}",
        "caption": f"{caption}"
    }
    })
    headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {access_token}'
    }

    # print(access_token," ACCESSSS************************",video_url)

    response = requests.request("POST", url, headers=headers, data=payload)
    print("completed sending video ",response.ok)


def run_llm(phone,text):
        # Prepare the conversation
    messages = [
        Message(role="system", content=f"""Story title : {text}
            Generate a short story with the title given above. This short story is for narrating. 
            The target audience and language of the story will be mentioned in the story else assume children and english.
            If hindi is mentioned then the text should be in हिंदी.
            
            Break the story into scenes such that each scene has at most 3 sentences. 
            Generate a dall-E prompt for each scene and include two keywords from below.
            Digital art,
            Photorealistic style,
            Anime movie,
            Synth wave,
            Van gogh,
            Picasso

            Please give output in JSON format. The JSON should be like this
            {{"scenes":[{{
                        "image_prompt": "dall-e image prompt",
                        "story_text": "scene dialogue",
                        "audio_model” :"choose from option below"
            }}]}}
            Audio_model can take four values based on language of the text. 
            If language of text is english then only choose english male or female. 
            English Male : v2/en_speaker_6
            English Female : v2/en_speaker_9
            Hindi Male : v2/hi_speaker_8
            Hindi Female : v2/hi_speaker_9 
            """
            ),
    ]


    options = Options(messages=messages,template="story-generator")

    # Interact with the service
    scenes_and_prompts = service.chat(options)
    print("*************",scenes_and_prompts.content)

  
    scenes_and_images = []
    # generate images for each of the prompt
    scenes_and_prompts_dict = json.loads(scenes_and_prompts.content)

    # scenes_and_prompts_dict = {
    #     "story_title": "Shiva - A Short Story in Hindi for Children", 
    #     "scenes": [
    #             {
    #                 "image_prompt": "Generate a digital art of Shiva meditating on Mount Kailash with a photorealistic style and snowy mountain background.", 
    #                 "story_text": "एक समय की बात है जब भगवान शिव दुनिया को अपनी ध्यान विचार में खो गए थे। उन्होंने माउंट कैलाश पर अपना आश्रम बनाया था जहाँ वे साधना करते रहते थे।", 
    #                 "audio_model": "hi_speaker_9"
    #             }, 
    #             {
    #                 "image_prompt": "Generate a pixel art of Shiva saving the world from disaster with the background of a Picasso painting.", 
    #                 "story_text": "एक दिन जब विश्व को आपदा का सामना करना पड़ा तब भगवान शिव ने लोगों की मदद करने की सोची। वे नागेश्त मंदिर से 5000 मील दूर एक रूसी दूतावास में जा बैठे थे और मेहमानों को इस संकट से निकालने के लिए प्रयास कर रहे थे।", 
    #                 "audio_model": "hi_speaker_8"
    #             }, 
    #             {
    #                 "image_prompt": "Generate an anime movie style artwork of Shiva dancing with Nandi.", 
    #                 "story_text": "शिव नाट्य और तांडव के प्रभावशाली नर्तक भी थे। उन्होंने नंदी के साथ नृत्य करने का भी आनंद लिया जो जानवरों में स्वर्गीय होने के कारण धार्मिक एवं सामाजिक संस्कार में महत्वपूर्ण माने जाते हैं।", 
    #                 "audio_model": "hi_speaker_9"
    #             },
    #             {
    #                 "image_prompt": "Generate a photorealistic style digital art of Shiva riding on Nandi with the background of a Synth wave sky.", 
    #                 "story_text": "नंदी को अपना वाहन बनाकर शिव बर्फ के शिखरों पर जाना लोगों के लिए एक पवित्र शाखा बन गए थे। उनके पास एक खास विशेषता थी कि वे वहां तक पहुंच सकते थे जहां कोई कोई नहीं जा सकता था।", 
    #                 "audio_model": "hi_speaker_8"
    #             }
    #         ]
    #     }
    

    scenes = scenes_and_prompts_dict['scenes']
    with concurrent.futures.ThreadPoolExecutor() as executor:
    # Submit tasks for each scene
        futures = [executor.submit(generate_image, scene) for scene in scenes]

    # Retrieve the results as they become available
    for future in concurrent.futures.as_completed(futures):
        try:
            scene_image = future.result()
            scenes_and_images.append(scene_image)
        except Exception as e:
            print(f"An error occurred: {e}")
    # for scene in scenes:
    #     scene_image = generate_image(scene)
    #     scenes_and_images.append(scene_image)

    finalPayload = {
        "scenes":scenes_and_images
    }

    print("Pinging karthik's laptop with payload ",finalPayload)

    try:
        # json_data = json.dumps(finalPayload)
        api_url = "https://b79c-49-207-201-12.ngrok-free.app/predict-script"
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(api_url, headers=headers, json=finalPayload)
        # print(response.content," ############################# karthik server response")
        video_url = save_video_from_response(response)
        send_video(phone,video_url,"your generated story for prompt : "+text+" is")
    except Exception as error:
        print("Error:", error)
    
    # Print the assistant's response
    print("We are done sending the whatsapp back to the user")
    send_text_message(phone,'Hope you enjoyed your video for prompt '+text)

def generate_image(scene):
    prompt = scene['image_prompt']
    print("Processing prompt",prompt)
    options = Options(prompt=prompt, size="1024x1024")
    prompt_response = service.generate_image(options)
    image_url = prompt_response.images[0]
    scene_image = {
        'image_url': image_url,
        'speaker_name': scene['audio_model'],# 'v2/en_speaker_9',
        'scene_description': scene['story_text']
    }
    return scene_image

@app.route('/', methods=['GET'])
def get_request():
    return 'Hello, World!'


@app.route('/whatsapp/webhook', methods=['GET'])
def get_request_webhook():
    name = request.args.get('hub.challenge')
    return name


@app.route('/testllm', methods=['GET'])
def test_llm():
    options = Options(prompt="jesus",size="1024x1024")
    prompt_response = service.generate_image(options)
    return prompt_response.images


@app.route('/whatsapp/webhook', methods=['POST'])
def post_request():
    data = request.get_json()

    if 'statuses' in data['entry'][0]['changes'][0]['value']:
        response = {'message': 'Message already received'}
        return jsonify(response)

    message_id = data['entry'][0]['changes'][0]['value']['messages'][0]['id']


    # if message_id in received_messages:
    #     print("this is already present")
    #     response = {'message': 'Message already received'}
    #     return jsonify(response)

    processed_message_ids = load_processed_message_ids()
    if message_id in processed_message_ids:
        print("this is already present ",message_id)
        response = {'message': 'Message already received'}
        return jsonify(response)

    # Add the message ID to the list of processed message IDs
    processed_message_ids.append(message_id)
    save_processed_message_ids(processed_message_ids)

    # Process the data as needed
    # ...
    print("Data being processed for the first time ************************", data)
    text_body = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
    whatsapp_id = data['entry'][0]['changes'][0]['value']['contacts'][0]['wa_id']
    phone = "+"+whatsapp_id
    # Store message ID in the map
    received_messages[message_id] = True

    print("Text received:", text_body)

    server_url_base = get_base_url()
    sample_video_url = server_url_base+"/static/sample_generated.mp4"
    send_text_message(phone,"Please wait...")
    send_video(phone,sample_video_url,"Here is a short story about sunrise for your kids")
    run_llm(phone,text_body)  # Call run_llm function with text_body
    # sendvideo(text_body)
    # video_url = save_video()
    response = {'message': 'Data received successfully'}
    return jsonify(response)

@app.route('/save_video', methods=['GET'])
def save_video():
    # Call the external API and get the video response
    api_response = requests.get('https://samplelib.com/lib/preview/mp4/sample-5s.mp4')

    # Extract the video data from the API response
    video_data = api_response.content

    # Generate a unique file name for the video
    video_file_name = generate_unique_file_name()

    # Create the 'static' directory if it doesn't exist
    static_directory = os.path.join(os.getcwd(), 'static')
    if not os.path.exists(static_directory):
        os.makedirs(static_directory)

    # Save the video data to a file on your server
    video_file_path = os.path.join(static_directory, video_file_name)
    with open(video_file_path, 'wb') as file:
        file.write(video_data)

    # Host the video file on your server
    # server_url_base = "https://ec83-125-23-34-124.ngrok-free.app"

    server_url_base = get_base_url()

    video_url = f'{server_url_base}/static/' + video_file_name
    print("Video will be saved to ",video_url)

    # Return the video URL as the response
    # return jsonify({'video_url': video_url}), 200
    return video_url

def get_base_url():
    if dev_environment == "development":
        server_url_base = "https://ec83-125-23-34-124.ngrok-free.app"
    else:
        server_url_base = "https://whatsapp-listener-78h6.onrender.com"
    return server_url_base

def save_video_from_response(api_response):
        # Extract the video data from the API response
    video_data = api_response.content

    # Generate a unique file name for the video
    video_file_name = generate_unique_file_name()

    # Create the 'static' directory if it doesn't exist
    static_directory = os.path.join(os.getcwd(), 'static')
    if not os.path.exists(static_directory):
        os.makedirs(static_directory)

    # Save the video data to a file on your server
    video_file_path = os.path.join(static_directory, video_file_name)
    with open(video_file_path, 'wb') as file:
        file.write(video_data)

    # Host the video file on your server
    # server_url_base = "https://ec83-125-23-34-124.ngrok-free.app"

    if dev_environment == "development":
        server_url_base = "https://ec83-125-23-34-124.ngrok-free.app"
    else:
        server_url_base = "https://whatsapp-listener-78h6.onrender.com"


    video_url = f'{server_url_base}/static/' + video_file_name
    print("Video will be saved to ",video_url)

    # Return the video URL as the response
    # return jsonify({'video_url': video_url}), 200
    return video_url

def generate_unique_file_name():
    timestamp = str(int(time.time()))  # Get current timestamp as a string
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))  # Generate a random string of length 6
    file_name = f"video_{timestamp}_{random_string}.mp4"  # Example file name format: video_1622235237_h3x8bo.mp4
    return file_name



def send_text_message(phone,text):
    print("SENDING TEXT MESSAGE ################ : ",text)
    url = 'https://graph.facebook.com/v16.0/100233876104846/messages'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    data = {
        "messaging_product": "whatsapp",    
        "recipient_type": "individual",
        "to": f"{phone}",
        "type": "text",
        "text": {
            "preview_url": True,
            "body": f"{text}"
        }
    }

    response = requests.post(url, headers=headers, json=data)
    print("Text message sent ",text,response.ok)

if __name__ == '__main__':
  app.run(host='0.0.0.0',port=5001, debug=True)


