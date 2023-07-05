import { interpolate, spring } from 'remotion';

import { useCurrentFrame, Audio, Sequence } from 'remotion';
import React from 'react';
import clsx from 'clsx';
import { base_url } from './db';

export const Word: React.FC<{
	scene: any;
	startFrame: number;
	endFrame: number;
	word: any;
	animationStartFrame: any;
	animationEndFrame: any;
}> = ({ scene, endFrame, startFrame, word, animationStartFrame, animationEndFrame }) => {
	const frame = useCurrentFrame();
	const opacity = interpolate(frame, [20, 40], [0, 1], {
		extrapolateLeft: 'clamp',
		extrapolateRight: 'clamp',
	});
	console.log(word.text, animationEndFrame, animationStartFrame)

	// Begin preset
	const scale1 = interpolate(frame, [animationStartFrame, (animationStartFrame + animationEndFrame) / 2, animationEndFrame], [100, 125, 100], { extrapolateRight: 'clamp', });
	// const translate1 = interpolate(frame, [startFrame, (endFrame + startFrame) / 2, endFrame], [0, 7, 0], { extrapolateRight: 'clamp', });
	// const rotate1 = interpolate(frame, [startFrame, (endFrame + startFrame) / 2, endFrame], [0, 10, 0], { extrapolateRight: 'clamp', });
	// End preset


	const isVisible = frame > startFrame && frame <= endFrame;
	const isBeingSpoken = frame > animationStartFrame && frame <= animationEndFrame;

	return (
		<div
			className={clsx(
				'text-gray-700 text-5xl font-bold leading-relaxed',
				isVisible ? '' : 'hidden'
			)}
			style={{
				padding: "0px 10px",
				color: !isBeingSpoken ? '#DBBA00' : '#FFD700',
				transform: isBeingSpoken ? `scale(${scale1}%)` : '',
			}}
		>
			{word.text}

		</div>
	);
};
