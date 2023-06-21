import Image from "next/image";
import ImageStack from "../components/ImageStack";
import { RemotionRoot } from "../remotion/Root";

const baseUrl = "https://45ac-49-207-203-60.ngrok-free.app/";
const json = {
  id: 11,
  scenes: [
    {
      audio_url: "audio/17.wav",
      background_image_prompt: "A disney castle in the distance, meadows",
      background_image_url: "images/17_background.png",
      created_at: "2023-05-31T07:26:42.666649",
      duration: 14.466666666666667,
      foreground_image_prompt: "Mickey mouse",
      foreground_image_url: "images/17_foreground.png",
      id: 17,
      scene_description:
        "Mickey Mouse was strolling down Main Street, USA, when he saw his friend Goofy. He waved to Goofy and shouted, 'HI GOOFY!' [laughs]",
      speaker_name: "v2/en_speaker_9",
    },
    {
      audio_url: "audio/18.wav",
      background_image_prompt: "An enchanted foerst with mushrooms",
      background_image_url: "images/18_background.png",
      created_at: "2023-05-31T07:26:42.666652",
      duration: 14.106666666666667,
      foreground_image_prompt: "Super Mario",
      foreground_image_url: "images/18_foreground.png",
      id: 18,
      scene_description:
        "Mickey Mouse and Goofy sat on a bench, talking about their exciting day. Mickey Mouse said, 'I went to the park and rode on all the rides.' Goofy replied, 'Wow! That sounds like so much fun!' [laughs]",
      speaker_name: "v2/en_speaker_9",
    },
  ],
  title: "Movie title",
};

const MakeVideo = () => {
  return <div>Enter {json.scenes[0].background_image_prompt} </div>;
};

export default MakeVideo;
