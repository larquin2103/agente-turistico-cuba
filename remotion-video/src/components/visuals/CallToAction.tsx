import { useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";
import type { Orientation } from "../../Video";
import { fontFamily } from "../../fonts";
import { visualBox } from "./_layout";

const DEMO_URL = "dentbotsonrisa.netlify.app";

export const CallToAction: React.FC<{
  orientation: Orientation;
  color: string;
}> = ({ orientation }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const ctaSpring = spring({ frame: frame - 10, fps, config: { damping: 12 } });
  const linkSpring = spring({ frame: frame - 26, fps, config: { damping: 13 } });

  const pulse = 1 + Math.sin(frame * 0.13) * 0.03;
  const glow = 0.4 + Math.sin(frame * 0.13) * 0.2;

  const linkSize = orientation === "portrait" ? 30 : 36;

  return (
    <div style={visualBox(orientation)}>
      <div
        style={{
          width: "100%",
          maxWidth: 760,
          margin: "0 auto",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          textAlign: "center",
          gap: 22,
        }}
      >
        {/* Label */}
        <div
          style={{
            fontSize: 13,
            color: "#888",
            fontFamily: fontFamily.mono,
            letterSpacing: 5,
            textTransform: "uppercase",
            opacity: interpolate(ctaSpring, [0, 1], [0, 1]),
          }}
        >
          ✦ Demo en vivo · gratis
        </div>

        {/* Big globe / icon */}
        <div
          style={{
            fontSize: orientation === "portrait" ? 56 : 64,
            opacity: interpolate(ctaSpring, [0, 1], [0, 1]),
            transform: `scale(${interpolate(ctaSpring, [0, 1], [0.6, 1])})`,
          }}
        >
          🌐
        </div>

        {/* Link button (single CTA) */}
        <div
          style={{
            opacity: interpolate(linkSpring, [0, 1], [0, 1]),
            transform: `scale(${
              interpolate(linkSpring, [0, 1], [0.85, 1]) * pulse
            })`,
            background:
              "linear-gradient(135deg, #4c9ac9 0%, #4cc9a8 100%)",
            color: "#03120f",
            padding: orientation === "portrait" ? "20px 28px" : "24px 40px",
            borderRadius: 18,
            fontSize: linkSize,
            fontFamily: fontFamily.mono,
            fontWeight: 700,
            letterSpacing: -0.5,
            display: "flex",
            alignItems: "center",
            gap: 14,
            boxShadow: `0 0 ${40 + glow * 40}px rgba(76,201,168,${glow})`,
            maxWidth: "100%",
            wordBreak: "break-all",
          }}
        >
          <span style={{ opacity: 0.6, fontSize: linkSize * 0.7 }}>https://</span>
          {DEMO_URL}
        </div>

        {/* Tagline */}
        <div
          style={{
            fontSize: orientation === "portrait" ? 20 : 22,
            color: "#f0ead8",
            fontFamily: fontFamily.display,
            fontStyle: "italic",
            opacity: interpolate(frame, [40, 58], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
          }}
        >
          “Tu agente listo en 15 minutos.”
        </div>

        {/* Chips */}
        <div
          style={{
            display: "flex",
            gap: 10,
            flexWrap: "wrap",
            justifyContent: "center",
            opacity: interpolate(frame, [52, 70], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
          }}
        >
          {["Sin contratos", "Operativo hoy", "Setup en 15 min"].map((t, i) => (
            <div
              key={i}
              style={{
                background: "rgba(255,255,255,0.05)",
                border: "1px solid rgba(255,255,255,0.12)",
                borderRadius: 999,
                padding: "7px 16px",
                fontSize: 14,
                color: "#ccc",
                fontFamily: fontFamily.body,
              }}
            >
              ✓ {t}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
