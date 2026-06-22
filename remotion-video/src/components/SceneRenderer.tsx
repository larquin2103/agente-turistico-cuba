import {
  AbsoluteFill,
  useCurrentFrame,
  interpolate,
  spring,
  useVideoConfig,
} from "remotion";
import type { Scene } from "../data/scenes";
import { actMeta } from "../data/scenes";
import type { Orientation } from "../Video";
import { fontFamily } from "../fonts";
import { SceneVisual } from "./visuals/SceneVisual";

export const SceneRenderer: React.FC<{
  scene: Scene;
  orientation: Orientation;
}> = ({ scene, orientation }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const isPortrait = orientation === "portrait";
  const meta = actMeta[scene.act];

  const bgPan = interpolate(frame, [0, durationInFrames], [0, 100]);

  // Title spring-in
  const titleSpring = spring({
    frame,
    fps,
    config: { damping: 16, stiffness: 70 },
  });
  const titleY = interpolate(titleSpring, [0, 1], [40, 0]);
  const titleOpacity = interpolate(titleSpring, [0, 1], [0, 1]);

  const badgeOpacity = interpolate(frame, [0, 14], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Narration fade-in
  const narrationDelay = 22;
  const narrationOpacity = interpolate(
    frame,
    [narrationDelay, narrationDelay + 22],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  const narrationY = interpolate(
    frame,
    [narrationDelay, narrationDelay + 22],
    [22, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Stat / hook pop-in
  const statDelay = 48;
  const statSpring = spring({
    frame: frame - statDelay,
    fps,
    config: { damping: 13, stiffness: 90 },
  });
  const statScale = interpolate(statSpring, [0, 1], [0.88, 1]);
  const statOpacity = interpolate(frame, [statDelay, statDelay + 16], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Scene exit fade
  const exitFade = interpolate(
    frame,
    [durationInFrames - 10, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const pad = isPortrait ? 56 : 84;
  const titleSize = isPortrait ? 60 : 56;
  const narrationSize = isPortrait ? 32 : 30;

  // ---- Reusable blocks ----------------------------------------------------

  const Header = (
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        opacity: badgeOpacity,
      }}
    >
      <div
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: 12,
          background: `${meta.badge}1a`,
          border: `1px solid ${meta.badge}66`,
          borderRadius: 999,
          padding: isPortrait ? "9px 18px" : "10px 22px",
          fontSize: isPortrait ? 17 : 18,
          fontFamily: fontFamily.mono,
          color: meta.badge,
          letterSpacing: 3,
          textTransform: "uppercase",
          fontWeight: 600,
        }}
      >
        <span style={{ fontSize: isPortrait ? 20 : 22 }}>{meta.emoji}</span>
        {meta.text}
      </div>
      <div
        style={{
          fontFamily: fontFamily.mono,
          color: "#666",
          fontSize: isPortrait ? 15 : 16,
          letterSpacing: 2,
        }}
      >
        ESC {String(scene.id).padStart(2, "0")} · {scene.time}
      </div>
    </div>
  );

  const Title = (
    <div
      style={{
        opacity: titleOpacity,
        transform: `translateY(${titleY}px)`,
      }}
    >
      <h1
        style={{
          margin: 0,
          fontFamily: fontFamily.display,
          fontSize: titleSize,
          fontWeight: 500,
          lineHeight: 1.08,
          color: "#f0ead8",
          letterSpacing: -0.5,
        }}
      >
        {scene.title}
      </h1>
      <div
        style={{
          height: 3,
          width: 72,
          background: scene.color,
          marginTop: 16,
          borderRadius: 2,
        }}
      />
    </div>
  );

  const Narration = (
    <div
      style={{
        opacity: narrationOpacity,
        transform: `translateY(${narrationY}px)`,
      }}
    >
      <div
        style={{
          fontSize: isPortrait ? 14 : 15,
          color: "#777",
          fontFamily: fontFamily.mono,
          letterSpacing: 4,
          textTransform: "uppercase",
          marginBottom: 10,
        }}
      >
        ▎ Narración
      </div>
      <div
        style={{
          fontSize: narrationSize,
          color: "#f0ead8",
          lineHeight: 1.45,
          fontStyle: "italic",
          fontFamily: fontFamily.display,
        }}
      >
        “{scene.narration}”
      </div>
    </div>
  );

  const StatHook = (scene.stat || scene.hook) && (
    <div
      style={{
        opacity: statOpacity,
        transform: `scale(${statScale})`,
        transformOrigin: "left center",
      }}
    >
      <div
        style={{
          background: `${scene.color}12`,
          border: `1px solid ${scene.color}55`,
          borderLeft: `4px solid ${scene.color}`,
          borderRadius: 12,
          padding: isPortrait ? "16px 20px" : "18px 24px",
          display: "flex",
          alignItems: "center",
          gap: 16,
        }}
      >
        <div style={{ fontSize: isPortrait ? 26 : 28 }}>
          {scene.stat ? "📊" : "⚡"}
        </div>
        <div style={{ flex: 1 }}>
          <div
            style={{
              fontSize: isPortrait ? 12 : 13,
              color: "#777",
              fontFamily: fontFamily.mono,
              letterSpacing: 3,
              textTransform: "uppercase",
              marginBottom: 5,
            }}
          >
            {scene.stat ? "Dato en pantalla" : "Texto impacto"}
          </div>
          <div
            style={{
              fontSize: isPortrait ? 22 : 23,
              color: scene.color,
              fontFamily: fontFamily.body,
              fontWeight: 600,
              lineHeight: 1.3,
            }}
          >
            {scene.stat || scene.hook}
          </div>
        </div>
      </div>
    </div>
  );

  // ---- Background ---------------------------------------------------------

  const background = (
    <>
      <AbsoluteFill
        style={{
          background: `radial-gradient(circle at ${50 + bgPan / 5}% ${
            50 - bgPan / 8
          }%, ${scene.bg} 0%, #050505 80%)`,
        }}
      />
      <div
        style={{
          position: "absolute",
          inset: 0,
          backgroundImage:
            "linear-gradient(rgba(255,255,255,0.015) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.015) 1px, transparent 1px)",
          backgroundSize: "60px 60px",
          opacity: 0.6,
        }}
      />
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          height: 4,
          background: `linear-gradient(90deg, transparent 0%, ${scene.color} 50%, transparent 100%)`,
          opacity: 0.8,
        }}
      />
    </>
  );

  // ---- Layout: PORTRAIT (stacked) -----------------------------------------

  if (isPortrait) {
    return (
      <AbsoluteFill
        style={{
          fontFamily: fontFamily.body,
          color: "#f0ead8",
          opacity: exitFade,
        }}
      >
        {background}
        <div
          style={{
            position: "absolute",
            top: pad,
            left: pad,
            right: pad,
            bottom: pad + 8,
            display: "flex",
            flexDirection: "column",
            gap: 22,
          }}
        >
          {Header}
          {Title}
          <div style={{ flex: 1, position: "relative", minHeight: 0 }}>
            <SceneVisual scene={scene} orientation={orientation} />
          </div>
          {Narration}
          {StatHook}
        </div>
      </AbsoluteFill>
    );
  }

  // ---- Layout: LANDSCAPE (two columns) ------------------------------------

  return (
    <AbsoluteFill
      style={{
        fontFamily: fontFamily.body,
        color: "#f0ead8",
        opacity: exitFade,
      }}
    >
      {background}

      {/* Header full width */}
      <div
        style={{
          position: "absolute",
          top: pad,
          left: pad,
          right: pad,
        }}
      >
        {Header}
      </div>

      {/* Two-column body */}
      <div
        style={{
          position: "absolute",
          top: pad + 64,
          left: pad,
          right: pad,
          bottom: pad,
          display: "flex",
          gap: 56,
          alignItems: "center",
        }}
      >
        {/* Left: text */}
        <div
          style={{
            flex: "0 0 41%",
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            gap: 28,
          }}
        >
          {Title}
          {Narration}
          {StatHook}
        </div>

        {/* Right: visual */}
        <div
          style={{
            flex: 1,
            position: "relative",
            alignSelf: "stretch",
            overflow: "hidden",
          }}
        >
          <SceneVisual scene={scene} orientation={orientation} />
        </div>
      </div>
    </AbsoluteFill>
  );
};
