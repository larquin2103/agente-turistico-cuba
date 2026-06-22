import { useCurrentFrame, interpolate } from "remotion";
import type { Orientation } from "../../Video";
import { fontFamily } from "../../fonts";
import { visualBox } from "./_layout";

const repetitiveQuestions = [
  "¿Cuánto cuesta una limpieza?",
  "¿Trabajan con seguro?",
  "¿Qué doctor atiende los sábados?",
  "¿Aceptan tarjeta?",
  "¿Tienen estacionamiento?",
  "¿Hacen blanqueamiento?",
  "¿Atienden niños?",
  "¿Cuánto tarda una endodoncia?",
];

export const TiredVsBot: React.FC<{
  orientation: Orientation;
  color: string;
}> = ({ orientation, color }) => {
  const frame = useCurrentFrame();

  return (
    <div style={visualBox(orientation)}>
      <div
        style={{
          display: "flex",
          flexDirection: orientation === "portrait" ? "column" : "row",
          gap: 30,
          width: "100%",
          maxWidth: 1100,
          margin: "0 auto",
          alignItems: "stretch",
        }}
      >
        {/* Left: chaos of questions */}
        <div
          style={{
            flex: 1,
            background: "#160a0a",
            border: "1px solid #e05c5c33",
            borderRadius: 16,
            padding: 22,
            position: "relative",
            overflow: "hidden",
            minHeight: 280,
          }}
        >
          <div
            style={{
              fontSize: 12,
              color: "#e05c5c",
              fontFamily: fontFamily.mono,
              letterSpacing: 3,
              marginBottom: 12,
            }}
          >
            ◉ EQUIPO HUMANO · DESBORDADO
          </div>
          <div
            style={{
              fontSize: 60,
              textAlign: "center",
              marginBottom: 8,
            }}
          >
            😩
          </div>
          <div
            style={{
              fontSize: 14,
              color: "#888",
              textAlign: "center",
              fontFamily: fontFamily.body,
              marginBottom: 16,
            }}
          >
            Repite lo mismo 30 veces al día
          </div>

          {/* Floating questions */}
          {repetitiveQuestions.map((q, i) => {
            const delay = i * 6;
            const startFrame = delay;
            const endFrame = delay + 80;
            const progress = interpolate(frame, [startFrame, endFrame], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            });
            const opacity =
              progress < 0.1
                ? progress * 10
                : progress > 0.85
                ? 1 - (progress - 0.85) * 6.67
                : 1;
            const yPos = 20 + (i % 4) * 30;
            const xPos = (i * 23) % 80;

            return (
              <div
                key={i}
                style={{
                  position: "absolute",
                  fontSize: 11,
                  color: "#e05c5cbb",
                  fontFamily: fontFamily.body,
                  background: "#28121299",
                  border: "1px solid #e05c5c33",
                  padding: "4px 9px",
                  borderRadius: 8,
                  bottom: `${yPos}%`,
                  left: `${10 + xPos / 2}%`,
                  opacity,
                  transform: `translateY(${-progress * 40}px)`,
                }}
              >
                {q}
              </div>
            );
          })}
        </div>

        {/* Right: calm bot */}
        <div
          style={{
            flex: 1,
            background: `${color}0d`,
            border: `1px solid ${color}55`,
            borderRadius: 16,
            padding: 22,
            minHeight: 280,
          }}
        >
          <div
            style={{
              fontSize: 12,
              color,
              fontFamily: fontFamily.mono,
              letterSpacing: 3,
              marginBottom: 12,
            }}
          >
            ✦ AGENTE IA · TRANQUILO
          </div>
          <div
            style={{
              fontSize: 60,
              textAlign: "center",
              marginBottom: 8,
            }}
          >
            🤖
          </div>
          <div
            style={{
              fontSize: 14,
              color: "#888",
              textAlign: "center",
              fontFamily: fontFamily.body,
              marginBottom: 16,
            }}
          >
            Responde igual la pregunta 1 o la 1000
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {[
              { q: "¿Cuánto cuesta una limpieza?", a: "$450 con detartraje." },
              { q: "¿Trabajan con seguro?", a: "Sí, AXA, GNP y MetLife." },
              { q: "¿Atienden sábados?", a: "Sí, de 9 AM a 2 PM con Dra. López." },
            ].map((qa, i) => (
              <div
                key={i}
                style={{
                  fontSize: 12,
                  fontFamily: fontFamily.body,
                  opacity: interpolate(frame, [40 + i * 12, 55 + i * 12], [0, 1], {
                    extrapolateLeft: "clamp",
                    extrapolateRight: "clamp",
                  }),
                }}
              >
                <div style={{ color: "#999", marginBottom: 2 }}>👤 {qa.q}</div>
                <div
                  style={{
                    color,
                    background: `${color}0d`,
                    padding: "5px 10px",
                    borderRadius: 6,
                    borderLeft: `2px solid ${color}`,
                  }}
                >
                  🤖 {qa.a}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
