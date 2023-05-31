'use client';
import React from 'react';
import { Composition } from 'remotion';
import { MyComposition } from './Composition';
import './../style.css';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="Empty"
        component={MyComposition}
        durationInFrames={60}
        fps={10}
        width={720}
        height={1280}
      />
    </>
  );
};
