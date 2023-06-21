import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {clsx} from 'clsx';
import {movie} from './db';
import {BgImage} from './BgImage';

export const MyComposition = () => {
	const frame = useCurrentFrame();

	const renderItems = () => {
		const renderedItems = [];
		const {scenes} = movie;
		let totalFramesTillNow = 0;
		for (let i = 0; i < scenes.length; i++) {
			const scene = scenes[i];
			const totalFramesInScene = Math.ceil(scene.duration) * 30;
			renderedItems.push(
				<BgImage
					scene={scene}
					key={i}
					startFrame={totalFramesTillNow}
					endFrame={totalFramesTillNow + totalFramesInScene}
				/>
			);

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
