import {interpolate} from 'remotion';
import {useCurrentFrame, Audio, Sequence} from 'remotion';
import React from 'react';
import clsx from 'clsx';
import {base_url} from './db';

export const BgImage: React.FC<{
	scene: any;
	startFrame: number;
	endFrame: number;
}> = ({scene, endFrame, startFrame}) => {
	const frame = useCurrentFrame();
	const opacity = interpolate(frame, [20, 40], [0, 1], {
		extrapolateLeft: 'clamp',
		extrapolateRight: 'clamp',
	});

	const isVisible = frame > startFrame && frame <= endFrame;

	return (
		<div
			// style={{opacity}}
			className={clsx(
				'absolute text-gray-700 text-5xl font-bold leading-relaxed',
				isVisible ? '' : 'hidden'
			)}
		>
			<div className="absolute">
				{startFrame} X {endFrame}
			</div>

			<img
				src={
					// 'https://picsum.photos/1280/720' ||
					`${base_url}/${scene.background_image_url}`
				}
			/>
			<Sequence from={startFrame} durationInFrames={endFrame - startFrame}>
				<Audio
					src={
						// 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3' ||
						`${base_url}/${scene.audio_url}`
					}
				/>
			</Sequence>
		</div>
	);
};
