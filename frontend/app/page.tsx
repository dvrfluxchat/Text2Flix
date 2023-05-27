"use client";
import { useState, FormEvent } from "react";
import { PlayCircle } from "react-feather";
import useLLM, { OpenAIMessage } from "usellm";

function isStringValidJson(str: string) {
  try {
    JSON.parse(str);
    return true;
  } catch (error) {
    return false;
  }
}

interface Scene {
  image_prompt: string;
  story_text: string;
}

interface Scenes {
  scenes: Scene[];
}

interface ScenePayload {
  image_url: string;
  speaker_name: string;
  scene_description: string;
}

interface ScenesPayload {
  scenes: ScenePayload[];
}

async function extractJson(llm: LLM, storyWithJson: string) {
  const userStory: OpenAIMessage = {
    content: storyWithJson.trim(),
    role: "user",
  };
  const chatHistory: OpenAIMessage[] = [
    {
      role: "assistant",
      content: `If there is a JSON array in the users input extract that text and just reply with that JSON. Otherwise if there is data according to the following JSON create the JSON array and respond with it.         
        Scene JSON.
        {
          "scene_description": "Scene description",
          "image_prompt": "dalle image prompt",
          "story_text": "scene text"
        }
        `,
    },
  ];

  chatHistory.push(userStory);

  const { message } = await llm.chat({
    messages: chatHistory,
    stream: false,
  });

  return message;
}

async function getStoryScenesJson(llm: LLM, userStoryPrompt: string) {
  const chatHistory: OpenAIMessage[] = [
    {
      role: "assistant",
      content: `Generate a short story about ${userStoryPrompt} for children with emphasis on words with CAPS . 
      Use [laughs] for laugther,  ... for pauses and [clears throat] for effect. 
      Break it down into scenes, and give one image prompt per scene for Dall-E 2. 
      The Dall-E prompt should describe the scene and also add these to the prompt "digital art,photorealistic style". 
      Do not use ambigous character names like rose and lily. 
      Please give the output in json format. 
      The json should be like this {"scenes":[{
          "image_prompt": "dalle image prompt",
          "story_text": "scene text"
          }]}
      make sure the story_text does not exceed 3 sentences.`,
    },
  ];

  // chatHistory.push(userStory);

  const { message } = await llm.chat({
    template: "story-generator",
    messages: chatHistory,
    stream: false,
  });

  console.log("story JSON", message.content);
  console.log(
    "Is JSON generated on first try ",
    isStringValidJson(message.content)
  );

  let jsonText = "{}";
  if (!isStringValidJson(message.content)) {
    const extractedJson = await extractJson(llm, message.content);
    console.log(
      "Is second JSON generated ",
      isStringValidJson(extractedJson.content)
    );
    console.log("SECOND JSON ", extractedJson.content);
    jsonText = extractedJson.content;
  } else {
    jsonText = message.content;
  }

  return JSON.parse(jsonText) as Scenes;
}

async function generateImagesForScenes(
  llm: LLM,
  scenes: Scenes,
  selectedSpeaker: string
) {
  const promises = scenes.scenes.map(async (scene) => {
    const { images } = await llm.generateImage({
      prompt: scene.image_prompt,
      size: "1024x1024",
    });
    const scenePayload: ScenePayload = {
      image_url: images[0],
      speaker_name: selectedSpeaker,
      scene_description: scene.story_text,
    };
    return scenePayload;
  });
  const jsonWithImages = await Promise.all(promises);
  const scenesPayload: ScenesPayload = {
    scenes: jsonWithImages,
  };
  return scenesPayload;
}

type LLM = ReturnType<typeof useLLM>;

export default function Home(): JSX.Element {
  const [textInput, setTextInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingText, setLoadingText] = useState("Loading");
  const [videoUrl, setVideoUrl] = useState(""); // Updated state for video URL

  const [selectedSpeaker, setSelectedSpeaker] = useState("v2/en_speaker_0"); // Default speaker
  const [generatedStory, setGeneratedStory] = useState("");

  const llm = useLLM({
    // serviceUrl: "https://usellm.org/api/llm", // For testing only. Follow this guide to create your own service URL: https://usellm.org/docs/api-reference/create-llm-service
    serviceUrl: "/api/llm",
  });

  const speakers = [
    { value: "v2/en_speaker_0", label: "Male Speaker 1" },
    { value: "v2/en_speaker_5", label: "Male Speaker 5" },
    { value: "v2/en_speaker_9", label: "Woman English Speaker" },
    // Add more speakers as needed
  ];

  const handleSubmit = async (
    event: FormEvent<HTMLFormElement>
  ): Promise<void> => {
    event.preventDefault();

    setLoading(true);
    setLoadingText("generating story content...");
    const storyScenesJson = await getStoryScenesJson(llm, textInput);
    // setGeneratedStory(JSON.stringify(storyScenesJson));

    setLoadingText("Generating images for story");
    const jsonWithImages = await generateImagesForScenes(
      llm,
      storyScenesJson,
      selectedSpeaker
    );
    console.log(JSON.stringify(jsonWithImages), "Generated images json");
    // setGeneratedStory(JSON.stringify(jsonWithImages));

    // const data = {
    //   text: textInput.trim(),
    //   speaker_name: selectedSpeaker,
    // };

    try {
      setLoadingText("Generating Video");
      const apiUrl = "https://b79c-49-207-201-12.ngrok-free.app/predict-script";
      const response = await fetch(apiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(jsonWithImages),
      });

      if (!response.ok) {
        throw new Error("Error: " + response.status);
      }

      const videoBlob = await response.blob(); // Fetch the video blob
      const videoUrl = URL.createObjectURL(videoBlob); // Create a URL for the video blob

      setVideoUrl(videoUrl); // Set the video URL
    } catch (error) {
      console.error("Error:", error);
      // Error handling
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gray-100">
      <header className="flex items-center mb-8">
        <PlayCircle size={32} className="mr-2 text-blue-500" />
        <h1 className="text-4xl font-bold text-blue-500 tracking-wider">
          Text2Flix
        </h1>
      </header>
      <form onSubmit={handleSubmit} className="flex flex-col">
        <textarea
          value={textInput}
          onChange={(e) => setTextInput(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-l focus:outline-none resize-none w-80 h-40 text-gray-800 mb-4"
        />
        <select
          value={selectedSpeaker}
          onChange={(e) => setSelectedSpeaker(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-l focus:outline-none w-80 text-gray-800 mb-4"
        >
          {speakers.map((speaker) => (
            <option key={speaker.value} value={speaker.value}>
              {speaker.label}
            </option>
          ))}
        </select>
        {loading ? (
          <button
            type="submit"
            disabled
            className="px-4 py-2 bg-blue-500 text-white rounded opacity-50 cursor-not-allowed"
          >
            {loadingText}
          </button>
        ) : (
          <button
            type="submit"
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 focus:outline-none"
          >
            Submit
          </button>
        )}

      </form>
      {videoUrl && (
          <div className="max-w-3xl max-h-full mx-auto mt-4">
            <video className="w-full h-auto" controls src={videoUrl}></video>
          </div>
        )}
      {generatedStory && (
        <p className="mt-4 text-gray-800 whitespace-pre-wrap">
          {generatedStory}
        </p>
      )}
    </div>
  );
}
