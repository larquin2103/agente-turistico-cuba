import { Composition } from "remotion";
import { PromoVideo } from "./Video";
import { FPS, totalDurationFrames } from "./data/scenes";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* Versión principal 16:9 — YouTube / Web / LinkedIn */}
      <Composition
        id="PromoVideo"
        component={PromoVideo}
        durationInFrames={totalDurationFrames}
        fps={FPS}
        width={1920}
        height={1080}
        defaultProps={{ orientation: "landscape" as const }}
      />

      {/* Versión vertical 9:16 — Reels / TikTok / Stories */}
      <Composition
        id="PromoVideoVertical"
        component={PromoVideo}
        durationInFrames={totalDurationFrames}
        fps={FPS}
        width={1080}
        height={1920}
        defaultProps={{ orientation: "portrait" as const }}
      />
    </>
  );
};
