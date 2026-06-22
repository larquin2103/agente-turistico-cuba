import { useCurrentFrame, interpolate } from "remotion";
import type { Orientation } from "../Video";

export const ProgressBar: React.FC<{
  totalFrames: number;
  orientation: Orientation;
}> = ({ totalFrames, orientation }) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [0, totalFrames], [0, 100], {
    extrapolateRight: "clamp",
  });

  const height = orientation === "portrait" ? 8 : 6;

  return (
    <div
      style={{
        position: "absolute",
        bottom: 0,
        left: 0,
        right: 0,
        height,
        background: "rgba(255,255,255,0.05)",
        zIndex: 100,
      }}
    >
      <div
        style={{
          height: "100%",
          width: `${progress}%`,
          background:
            "linear-gradient(90deg, #c9a84c 0%, #e05c5c 25%, #4c9ac9 50%, #c94c7a 75%, #a84cc9 100%)",
          transition: "width 50ms linear",
        }}
      />
    </div>
  );
};
