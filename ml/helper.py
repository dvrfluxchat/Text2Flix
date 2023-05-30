import os
import requests
import io
import base64
from PIL import Image, PngImagePlugin
DEFAULT_WEBUI_IP = "http://127.0.0.1:7860"

def generate_img_using_sdapi(
        prompt,
        output_loc,
        idx
    ):
    payload = {
        "prompt": prompt,
        "steps": 50,
        "batch_size": 1,
        "cfg_scale": 7.5,
        "sampler_index": "DDIM",
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
    image.save(image_path, pnginfo=pnginfo)
    return image_path