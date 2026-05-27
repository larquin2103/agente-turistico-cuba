import { useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";
import type { Orientation } from "../../Video";
import { fontFamily } from "../../fonts";
import { visualBox } from "./_layout";

export const ProblemPhone: React.FC<{ orientation: Orientation }> = ({
  orientation,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const phoneIn = spring({ frame: frame - 10, fps, config: { damping: 14 } });
  const phoneY = interpolate(phoneIn, [0, 1], [60, 0]);
  const phoneOpacity = interpolate(phoneIn, [0, 1], [0, 1]);

  // Vibrate effect
  const vibrate = Math.sin(frame * 0.8) * (frame > 30 && frame < 80 ? 4 : 0);

  // Time digital clock
  const minutes = 30 + Math.floor(frame / 60);
  const timeStr = `23:${String(minutes).padStart(2, "0")}`;

  return (
    <div style={visualBox(orientation)}>
      <div
        style={{
          width: orientation === "portrait" ? 360 : 380,
          height: orientation === "portrait" ? 560 : 580,
          background: "#0d0d0d",
          border: "6px solid #1a1a1a",
          borderRadius: 48,
          padding: 24,
          opacity: phoneOpacity,
          transform: `translate(${vibrate}px, ${phoneY}px) rotate(${vibrate / 8}deg)`,
          boxShadow: `0 0 80px rgba(224,92,92,0.15), inset 0 0 40px rgba(0,0,0,0.5)`,
          position: "relative",
          fontFamily: fontFamily.body,
        }}
      >
        {/* Notch */}
        <div
          style={{
            width: 100,
            height: 26,
            background: "#000",
            borderRadius: 999,
            margin: "0 auto 18px",
          }}
        />

        {/* Clock */}
        <div
          style={{
            textAlign: "center",
            fontSize: 14,
            color: "#888",
            fontFamily: fontFamily.mono,
            marginBottom: 8,
          }}
        >
          Lunes · {timeStr}
        </div>

        {/* Incoming call */}
        <div
          style={{
            background: "#1f0a0a",
            border: "1px solid #e05c5c55",
            borderRadius: 18,
            padding: 18,
            marginBottom: 14,
            opacity: interpolate(frame, [25, 40], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
          }}
        >
          <div
            style={{
              fontSize: 11,
              color: "#e05c5c",
              fontFamily: fontFamily.mono,
              letterSpacing: 2,
              marginBottom: 4,
            }}
          >
            ◉ LLAMADA PERDIDA
          </div>
          <div style={{ fontSize: 18, color: "#fff", fontWeight: 600 }}>
            Usuario sin atender
          </div>
          <div style={{ fontSize: 12, color: "#888", marginTop: 2 }}>
            +53 5 384 2190
          </div>
        </div>

        {/* WhatsApp messages */}
        <div
          style={{
            background: "#0a1a0f",
            border: "1px solid #25d36622",
            borderRadius: 18,
            padding: 16,
            opacity: interpolate(frame, [50, 70], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
          }}
        >
          <div
            style={{
              fontSize: 11,
              color: "#25d366",
              fontFamily: fontFamily.mono,
              letterSpacing: 2,
              marginBottom: 8,
            }}
          >
            ● WHATSAPP · 3 sin leer
          </div>
          {[
            "Hola, ¿siguen abiertos?",
            "¿Tienen cita disponible mañana?",
            "Hola? Necesito ayuda…",
          ].map((msg, i) => (
            <div
              key={i}
              style={{
                background: "#143d2a",
                borderRadius: 12,
                padding: "8px 12px",
                fontSize: 13,
                color: "#d4f0d8",
                marginBottom: 6,
                maxWidth: "85%",
                opacity: interpolate(
                  frame,
                  [60 + i * 8, 70 + i * 8],
                  [0, 1],
                  { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
                ),
              }}
            >
              {msg}
              <span
                style={{
                  fontSize: 10,
                  color: "#7a8c80",
                  marginLeft: 8,
                  letterSpacing: 1,
                }}
              >
                ✓✓
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
