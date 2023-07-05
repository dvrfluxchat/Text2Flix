import { AbsoluteFill, useCurrentFrame } from 'remotion';
import { clsx } from 'clsx';
import { movie } from './db';
import { BgImage } from './BgImage';
import { Word } from './Subtitles';

export const MyComposition = () => {
	const frame = useCurrentFrame();

	const renderItems = () => {

		const renderedItems = [];
		const { scenes } = movie;
		let totalFramesTillNow = 0;
		for (let i = 0; i < scenes.length; i++) {
			const scene = scenes[i];
			const totalFramesInScene = Math.ceil(scene.duration) * 30; // 30 fps
			renderedItems.push(
				<BgImage
					scene={scene}
					key={i}
					startFrame={totalFramesTillNow}
					endFrame={totalFramesTillNow + totalFramesInScene}
				/>

			);
			for (let j = 0; j < scene.audio_timestamp.segments.length; j++) {
				const segment = scene.audio_timestamp.segments[j];
				let numWords = 4;
				for (let k = 0; k < segment.words.length; k = k + numWords) {
					const wordsseleted = segment.words.slice(k, k + numWords);
					const startTemp = wordsseleted[0].start;
					const endTemp = wordsseleted[wordsseleted.length - 1].end;
					let wordsGrouped = [];
					let wordsFrameTillNow = 0;
					for (let l = 0; l < wordsseleted.length; l++) {
						let animationStartFrame = totalFramesTillNow + startTemp * 30 + wordsFrameTillNow;
						let animationEndFrame = animationStartFrame + (wordsseleted[l].end - wordsseleted[l].start) * 30;
						wordsGrouped.push(<Word
							scene={scene}
							key={i.toString() + j.toString() + k.toString() + l.toString()}
							startFrame={totalFramesTillNow + startTemp * 30}
							endFrame={totalFramesTillNow + endTemp * 30}
							animationEndFrame={animationEndFrame}
							animationStartFrame={animationStartFrame}
							word={wordsseleted[l]}
						/>);
						wordsFrameTillNow += (wordsseleted[l].end - wordsseleted[l].start) * 30;
					}
					renderedItems.push(
						<div className='absolute' style={{ width: "400px", display: "flex", flexWrap: "wrap", justifyContent: "center" }}>
							{wordsGrouped}
						</div>
					)
				}
			}


			totalFramesTillNow += totalFramesInScene;
		}

		return renderedItems;
	};

	return (
		<AbsoluteFill
			className={clsx('bg-gray-100 items-center justify-center', frame > 240)}
		>
			{renderItems()}
		</AbsoluteFill>
	);
};
