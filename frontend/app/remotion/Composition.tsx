'use client';
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from 'remotion';
import ImageStack from '../components/ImageStack';
export const MyComposition = () => {
  const { fps, durationInFrames, width, height } = useVideoConfig();
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill
      style={{
        justifyContent: 'center',
        alignItems: 'center',
        fontSize: 60,
        backgroundColor: 'white',
      }}
    >
      This {width}x{height}px video is {durationInFrames / fps} second long with
      current frame {frame}.
      <div>
        <p className="text-red-400">Hola red</p>
        <ImageStack
          imageUrls={[
            'https://45ac-49-207-203-60.ngrok-free.app/images/17_background.png',
            'https://45ac-49-207-203-60.ngrok-free.app/images/17_foreground.png',
          ]}
        />
      </div>
    </AbsoluteFill>
  );
};
