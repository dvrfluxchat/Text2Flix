"use client";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import ImageStack from "../components/ImageStack";
export const MyComposition = () => {
  const { fps, durationInFrames, width, height } = useVideoConfig();
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        fontSize: 60,
        backgroundColor: "white",
      }}
    >
      This {width}x{height}px video is {durationInFrames / fps} second long with
      current frame {frame}.
      <div>
        <p className="text-red-400">Hola red</p>
      </div>
    </AbsoluteFill>
  );
};
