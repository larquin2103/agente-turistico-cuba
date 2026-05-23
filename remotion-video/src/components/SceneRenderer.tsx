import { AbsoluteFill, useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";
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

  // Animated background gradient
  const bgPan = interpolate(frame, [0, durationInFrames], [0, 100]);

  // Title spring-in
  const titleSpring = spring({
    frame,
    fps,
    config: { damping: 14, stiffness: 80 },
  });
  const titleY = interpolate(titleSpring, [0, 1], [40, 0]);
  const titleOpacity = interpolate(titleSpring, [0, 1], [0, 1]);

  // Badge fade
  const badgeOpacity = interpolate(frame, [0, 12], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Narration fade-in (after title)
  const narrationDelay = 20;
  const narrationOpacity = interpolate(
    frame,
    [narrationDelay, narrationDelay + 20],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  const narrationY = interpolate(
    frame,
    [narrationDelay, narrationDelay + 20],
    [20, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Stat / hook box pop-in (later)
  const statDelay = 50;
  const statSpring = spring({
    frame: frame - statDelay,
    fps,
    config: { damping: 12, stiffness: 100 },
  });
  const statScale = interpolate(statSpring, [0, 1], [0.85, 1]);
  const statOpacity = interpolate(frame, [statDelay, statDelay + 15], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Scene exit fade
  const exitFade = interpolate(
    frame,
    [durationInFrames - 8, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const padding = isPortrait ? 60 : 90;
  const titleSize = isPortrait ? 64 : 76;
  const narrationSize = isPortrait ? 32 : 36;

  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(circle at ${50 + bgPan / 5}% ${
          50 - bgPan / 8
        }%, ${scene.bg} 0%, #050505 80%)`,
        opacity: exitFade,
        fontFamily: fontFamily.body,
        color: "#f0ead8",
      }}
    >
      {/* Subtle grid overlay */}
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

      {/* Top accent line */}
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

      {/* HEADER: badge + scene number + time */}
      <div
        style={{
          position: "absolute",
          top: padding,
          left: padding,
          right: padding,
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
            gap: 14,
            background: `${meta.badge}1a`,
            border: `1px solid ${meta.badge}66`,
            borderRadius: 999,
            padding: isPortrait ? "10px 20px" : "12px 26px",
            fontSize: isPortrait ? 18 : 20,
            fontFamily: fontFamily.mono,
            color: meta.badge,
            letterSpacing: 3,
            textTransform: "uppercase",
            fontWeight: 600,
          }}
        >
          <span style={{ fontSize: isPortrait ? 22 : 24 }}>{meta.emoji}</span>
          {meta.text}
        </div>

        <div
          style={{
            fontFamily: fontFamily.mono,
            color: "#666",
            fontSize: isPortrait ? 16 : 18,
            letterSpacing: 2,
          }}
        >
          ESC {String(scene.id).padStart(2, "0")} · {scene.time}
        </div>
      </div>

      {/* TITLE */}
      <div
        style={{
          position: "absolute",
          top: isPortrait ? padding + 100 : padding + 110,
          left: padding,
          right: padding,
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
            lineHeight: 1.05,
            color: "#f0ead8",
            letterSpacing: -0.5,
            maxWidth: isPortrait ? "100%" : "75%",
          }}
        >
          {scene.title}
        </h1>
        <div
          style={{
            height: 3,
            width: 80,
            background: scene.color,
            marginTop: 18,
            borderRadius: 2,
          }}
        />
      </div>

      {/* CENTER: visual */}
      <SceneVisual scene={scene} orientation={orientation} />

      {/* NARRATION */}
      <div
        style={{
          position: "absolute",
          bottom: scene.stat || scene.hook ? (isPortrait ? 380 : 260) : (isPortrait ? 200 : 140),
          left: padding,
          right: padding,
          opacity: narrationOpacity,
          transform: `translateY(${narrationY}px)`,
        }}
      >
        <div
          style={{
            fontSize: isPortrait ? 14 : 16,
            color: "#666",
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
            lineHeight: 1.4,
            fontStyle: "italic",
            fontFamily: fontFamily.display,
            maxWidth: isPortrait ? "100%" : "85%",
          }}
        >
          “{scene.narration}”
        </div>
      </div>

      {/* STAT / HOOK box */}
      {(scene.stat || scene.hook) && (
        <div
          style={{
            position: "absolute",
            bottom: isPortrait ? 140 : 80,
            left: padding,
            right: padding,
            opacity: statOpacity,
            transform: `scale(${statScale})`,
            transformOrigin: "left center",
          }}
        >
          <div
            style={{
              background: `${scene.color}10`,
              border: `1px solid ${scene.color}55`,
              borderLeft: `4px solid ${scene.color}`,
              borderRadius: 12,
              padding: isPortrait ? "18px 24px" : "22px 30px",
              display: "flex",
              alignItems: "center",
              gap: 18,
              backdropFilter: "blur(8px)",
            }}
          >
            <div
              style={{
                fontSize: isPortrait ? 28 : 32,
              }}
            >
              {scene.stat ? "📊" : "⚡"}
            </div>
            <div style={{ flex: 1 }}>
              <div
                style={{
                  fontSize: isPortrait ? 13 : 14,
                  color: "#666",
                  fontFamily: fontFamily.mono,
                  letterSpacing: 3,
                  textTransform: "uppercase",
                  marginBottom: 6,
                }}
              >
                {scene.stat ? "Dato en pantalla" : "Texto impacto"}
              </div>
              <div
                style={{
                  fontSize: isPortrait ? 24 : 28,
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
      )}
    </AbsoluteFill>
  );
};
