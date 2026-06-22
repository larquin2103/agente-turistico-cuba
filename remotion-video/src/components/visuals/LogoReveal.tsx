import { useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";
import type { Orientation } from "../../Video";
import { fontFamily } from "../../fonts";
import { visualBox } from "./_layout";

export const LogoReveal: React.FC<{
  orientation: Orientation;
  color: string;
}> = ({ orientation, color }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const logoSpring = spring({
    frame: frame - 10,
    fps,
    config: { damping: 12, stiffness: 80 },
  });
  const logoScale = interpolate(logoSpring, [0, 1], [0.3, 1]);
  const logoOpacity = interpolate(logoSpring, [0, 1], [0, 1]);

  // Ring rotation
  const ringRotation = frame * 1.5;

  // Pulsing glow
  const glowPulse = 0.4 + Math.sin(frame * 0.1) * 0.2;

  // Subtitle reveal
  const subtitleOpacity = interpolate(frame, [40, 60], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div style={visualBox(orientation)}>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 30,
          opacity: logoOpacity,
        }}
      >
        {/* Logo mark */}
        <div
          style={{
            position: "relative",
            width: orientation === "portrait" ? 240 : 280,
            height: orientation === "portrait" ? 240 : 280,
            transform: `scale(${logoScale})`,
          }}
        >
          {/* Outer rotating ring */}
          <div
            style={{
              position: "absolute",
              inset: 0,
              borderRadius: "50%",
              border: `2px dashed ${color}66`,
              transform: `rotate(${ringRotation}deg)`,
            }}
          />
          {/* Glow */}
          <div
            style={{
              position: "absolute",
              inset: 20,
              borderRadius: "50%",
              background: `radial-gradient(circle, ${color}55 0%, ${color}00 70%)`,
              opacity: glowPulse,
            }}
          />
          {/* Inner circle */}
          <div
            style={{
              position: "absolute",
              inset: 40,
              borderRadius: "50%",
              background: `linear-gradient(135deg, ${color} 0%, ${color}aa 100%)`,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: orientation === "portrait" ? 90 : 110,
              boxShadow: `0 0 60px ${color}88`,
            }}
          >
            🤖
          </div>
        </div>

        {/* Tagline */}
        <div
          style={{
            textAlign: "center",
            opacity: subtitleOpacity,
          }}
        >
          <div
            style={{
              fontSize: orientation === "portrait" ? 36 : 46,
              fontFamily: fontFamily.display,
              color: "#f0ead8",
              fontWeight: 500,
              letterSpacing: -0.5,
            }}
          >
            Agente IA <span style={{ color }}>24/7</span>
          </div>
          <div
            style={{
              display: "flex",
              gap: 18,
              justifyContent: "center",
              marginTop: 16,
              fontFamily: fontFamily.mono,
              fontSize: 18,
              color: "#aaa",
            }}
          >
            <span style={{ color: "#25d366" }}>● WhatsApp</span>
            <span style={{ color: "#666" }}>·</span>
            <span style={{ color: "#0088cc" }}>● Telegram</span>
          </div>
        </div>
      </div>
    </div>
  );
};
