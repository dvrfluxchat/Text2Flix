'use client';
import { Img } from 'remotion';

interface ImageStackProps {
  imageUrls: string[];
}

const ImageStack: React.FC<ImageStackProps> = ({ imageUrls }) => {
  return (
    <div style={{ position: 'relative' }}>
      {imageUrls.map((url, index) => (
        <Img
          key={index}
          src={url}
          alt={`Image ${index + 1}`}
          //   width={1280}
          //   height={720}
          className="absolute inset-0"
        />
      ))}
    </div>
  );
};

export default ImageStack;
