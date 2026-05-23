import { AbsoluteFill, Series, useVideoConfig } from "remotion";
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
        {scenes.map((scene) => (
          <Series.Sequence
            key={scene.id}
            durationInFrames={scene.duration * FPS}
          >
            <SceneRenderer scene={scene} orientation={orientation} />
          </Series.Sequence>
        ))}
      </Series>

      <ProgressBar
        totalFrames={durationInFrames}
        orientation={orientation}
      />
    </AbsoluteFill>
  );
};
