import { useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";
import type { Orientation } from "../../Video";
import { fontFamily } from "../../fonts";
import { visualBox } from "./_layout";

export const GroundedBot: React.FC<{
  orientation: Orientation;
  color: string;
}> = ({ orientation, color }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const bubbleSpring = spring({ frame: frame - 15, fps, config: { damping: 13 } });

  return (
    <div style={visualBox(orientation)}>
      <div
        style={{
          width: "100%",
          maxWidth: 900,
          margin: "0 auto",
          display: "flex",
          flexDirection: "column",
          gap: 14,
        }}
      >
        {/* User question */}
        <div
          style={{
            alignSelf: "flex-start",
            background: "#1f2c33",
            color: "#e9edef",
            padding: "14px 18px",
            borderRadius: 14,
            borderTopLeftRadius: 4,
            fontSize: 18,
            maxWidth: "75%",
            fontFamily: fontFamily.body,
            opacity: interpolate(frame, [10, 25], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
          }}
        >
          ¿A qué hora abre la sucursal de Polanco?
        </div>

        {/* Bot honest response */}
        <div
          style={{
            alignSelf: "flex-end",
            background: `${color}15`,
            color: "#f0ead8",
            border: `1px solid ${color}66`,
            padding: "16px 20px",
            borderRadius: 14,
            borderTopRightRadius: 4,
            fontSize: 17,
            maxWidth: "75%",
            fontFamily: fontFamily.body,
            opacity: interpolate(bubbleSpring, [0, 1], [0, 1]),
            transform: `scale(${interpolate(bubbleSpring, [0, 1], [0.9, 1])})`,
            lineHeight: 1.5,
          }}
        >
          <div
            style={{
              fontFamily: fontFamily.mono,
              fontSize: 11,
              color,
              letterSpacing: 2,
              marginBottom: 6,
            }}
          >
            🤖 AGENTE — RESPUESTA HONESTA
          </div>
          No tengo esa información en mi base de conocimiento.
          <br />
          <span style={{ color: "#aaa", fontSize: 15 }}>
            Te conecto con un asesor humano ahora mismo. 👇
          </span>
        </div>

        {/* Anti-feature checks */}
        <div
          style={{
            marginTop: 18,
            display: "grid",
            gridTemplateColumns:
              orientation === "portrait" ? "1fr" : "repeat(3, 1fr)",
            gap: 12,
          }}
        >
          {[
            { icon: "✗", text: "Cero respuestas inventadas" },
            { icon: "✗", text: "Cero precios incorrectos" },
            { icon: "✗", text: "Cero malentendidos" },
          ].map((c, i) => (
            <div
              key={i}
              style={{
                background: `${color}0d`,
                border: `1px solid ${color}33`,
                borderRadius: 10,
                padding: "12px 14px",
                display: "flex",
                alignItems: "center",
                gap: 10,
                opacity: interpolate(frame, [50 + i * 8, 65 + i * 8], [0, 1], {
                  extrapolateLeft: "clamp",
                  extrapolateRight: "clamp",
                }),
              }}
            >
              <div
                style={{
                  width: 28,
                  height: 28,
                  borderRadius: "50%",
                  background: color,
                  color: "#000",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontWeight: 700,
                  fontSize: 14,
                  flexShrink: 0,
                }}
              >
                {c.icon}
              </div>
              <div
                style={{
                  fontSize: 14,
                  color: "#ccc",
                  fontFamily: fontFamily.body,
                }}
              >
                {c.text}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
