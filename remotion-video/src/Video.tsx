import {
  AbsoluteFill,
  Audio,
  Series,
  staticFile,
  useVideoConfig,
} from "remotion";
import { scenes, FPS } from "./data/scenes";
import { SceneRenderer } from "./components/SceneRenderer";
import { ProgressBar } from "./components/ProgressBar";
import { loadFonts } from "./fonts";

loadFonts();

export type Orientation = "landscape" | "portrait";

export const PromoVideo: React.FC<{ orientation: Orientation }> = ({
  orientation,
}) => {
  const { durationInFrames } = useVideoConfig();

  return (
    <AbsoluteFill style={{ background: "#050505", overflow: "hidden" }}>
      <Series>
        {scenes.map((scene) => {
          const audioName = `voz-${String(scene.id).padStart(2, "0")}.wav`;
          return (
            <Series.Sequence
              key={scene.id}
              durationInFrames={scene.duration * FPS}
            >
              <SceneRenderer scene={scene} orientation={orientation} />
              <Audio src={staticFile(`audio/${audioName}`)} volume={1} />
            </Series.Sequence>
          );
        })}
      </Series>

      <ProgressBar
        totalFrames={durationInFrames}
        orientation={orientation}
      />
    </AbsoluteFill>
  );
};
