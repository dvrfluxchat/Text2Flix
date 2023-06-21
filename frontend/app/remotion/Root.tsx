import { Composition } from "remotion";
import { HelloWorld } from "../components/HelloWorld";
import { Logo } from "../components/HelloWorld/Logo";
import "../style.css";
import ImageStack from "../components/ImageStack";
// Each <Composition> is an entry in the sidebar!

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        // You can take the "id" to render a video:
        // npx remotion render src/index.ts <id> out/video.mp4
        id="HelloWorld"
        component={HelloWorld}
        durationInFrames={150}
        fps={30}
        width={1920}
        height={1080}
        // You can override these props for each render:
        // https://www.remotion.dev/docs/parametrized-rendering
        defaultProps={{
          titleText: "Welcome to Remotion",
          titleColor: "black",
        }}
      />
      {/* Mount any React component to make it show up in the sidebar and work on it individually! */}
      <Composition
        id="OnlyLogo"
        component={Logo}
        durationInFrames={150}
        fps={30}
        width={1920}
        height={1080}
      />

      <Composition
        id="ImageStack"
        component={ImageStack}
        durationInFrames={150}
        fps={30}
        width={720}
        height={1280}
        defaultProps={{
          fg: "https://45ac-49-207-203-60.ngrok-free.app/images/17_foreground.png",
          bg: "https://45ac-49-207-203-60.ngrok-free.app/images/17_background.png",
        }}
      />
    </>
  );
};
