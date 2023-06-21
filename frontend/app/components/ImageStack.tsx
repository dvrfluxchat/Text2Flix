"use client";
import { AbsoluteFill, Img } from "remotion";

interface ImageStackProps {
  bg: string;
  fg: string;
}

const ImageStack: React.FC<ImageStackProps> = ({ bg, fg }) => {
  const zoomlevel = 100;
  return (
    <AbsoluteFill>
      <Img
        src={bg}
        alt={`Image background`}
        className={`absolute inset-0 w-[${zoomlevel}%] h-[${zoomlevel}%] object-cover`}
      />
      <Img
        src={fg}
        alt={`Image Foreground`}
        width={720}
        height={1280}
        className="absolute inset-0 w-full h-full object-cover"
      />
      <p className="absolute text-9xl text-yellow-400 font-bold">test</p>
    </AbsoluteFill>
  );
};

export default ImageStack;
