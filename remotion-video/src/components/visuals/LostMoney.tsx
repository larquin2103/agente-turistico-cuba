import { useCurrentFrame, interpolate, useVideoConfig } from "remotion";
import type { Orientation } from "../../Video";
import { fontFamily } from "../../fonts";
import { visualBox } from "./_layout";

const stats = [
  { label: "Llamadas perdidas", value: 12, suffix: "/día" },
  { label: "Mensajes sin responder", value: 47, suffix: "/día" },
  { label: "Citas canceladas", value: 8, suffix: "/semana" },
];

export const LostMoney: React.FC<{ orientation: Orientation }> = ({
  orientation,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  // Animated counter
  const progress = interpolate(frame, [10, 90], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Declining graph points
  const graphPoints = Array.from({ length: 10 }).map((_, i) => {
    const baseY = 30 + i * 5;
    const offset = Math.sin(i * 0.7) * 8;
    return { x: i * 11, y: baseY + offset };
  });

  const graphProgress = interpolate(frame, [20, durationInFrames - 10], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div style={visualBox(orientation)}>
      <div
        style={{
          display: "flex",
          flexDirection: orientation === "portrait" ? "column" : "row",
          gap: 30,
          alignItems: "stretch",
          width: "100%",
          maxWidth: orientation === "portrait" ? 600 : 1100,
          margin: "0 auto",
        }}
      >
        {/* Stats column */}
        <div
          style={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            gap: 14,
          }}
        >
          {stats.map((s, i) => {
            const animatedVal = Math.floor(s.value * progress);
            const delayedOpacity = interpolate(
              frame,
              [15 + i * 8, 30 + i * 8],
              [0, 1],
              { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
            );
            return (
              <div
                key={i}
                style={{
                  background: "#1a0a0a",
                  border: "1px solid #e05c5c55",
                  borderRadius: 14,
                  padding: "20px 24px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  opacity: delayedOpacity,
                }}
              >
                <div
                  style={{
                    fontSize: 16,
                    color: "#bbb",
                    fontFamily: fontFamily.body,
                  }}
                >
                  {s.label}
                </div>
                <div
                  style={{
                    fontSize: 42,
                    color: "#e05c5c",
                    fontFamily: fontFamily.mono,
                    fontWeight: 700,
                    letterSpacing: -1,
                  }}
                >
                  {animatedVal}
                  <span
                    style={{
                      fontSize: 16,
                      color: "#e05c5c99",
                      marginLeft: 4,
                    }}
                  >
                    {s.suffix}
                  </span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Declining graph */}
        <div
          style={{
            flex: 1,
            background: "#0d0606",
            border: "1px solid #e05c5c33",
            borderRadius: 14,
            padding: 24,
            position: "relative",
          }}
        >
          <div
            style={{
              fontSize: 12,
              color: "#888",
              fontFamily: fontFamily.mono,
              letterSpacing: 2,
              marginBottom: 8,
            }}
          >
            ATENCIÓN OPORTUNA · ÚLTIMOS 10 DÍAS
          </div>
          <div style={{ fontSize: 28, color: "#e05c5c", fontWeight: 700 }}>
            ↓ −34%
          </div>

          <svg
            viewBox="0 0 110 90"
            style={{
              width: "100%",
              height: orientation === "portrait" ? 160 : 200,
              marginTop: 12,
            }}
            preserveAspectRatio="none"
          >
            <defs>
              <linearGradient id="fadeRed" x1="0" x2="0" y1="0" y2="1">
                <stop offset="0%" stopColor="#e05c5c" stopOpacity="0.4" />
                <stop offset="100%" stopColor="#e05c5c" stopOpacity="0" />
              </linearGradient>
            </defs>
            {/* Area */}
            <path
              d={`M 0 90 ${graphPoints
                .slice(0, Math.ceil(graphPoints.length * graphProgress))
                .map((p) => `L ${p.x} ${p.y}`)
                .join(" ")} L ${
                graphPoints[Math.ceil(graphPoints.length * graphProgress) - 1]
                  ?.x || 0
              } 90 Z`}
              fill="url(#fadeRed)"
            />
            {/* Line */}
            <path
              d={`M 0 30 ${graphPoints
                .slice(0, Math.ceil(graphPoints.length * graphProgress))
                .map((p) => `L ${p.x} ${p.y}`)
                .join(" ")}`}
              stroke="#e05c5c"
              strokeWidth="1.5"
              fill="none"
            />
            {/* Dots */}
            {graphPoints
              .slice(0, Math.ceil(graphPoints.length * graphProgress))
              .map((p, i) => (
                <circle
                  key={i}
                  cx={p.x}
                  cy={p.y}
                  r="1.2"
                  fill="#e05c5c"
                />
              ))}
          </svg>
        </div>
      </div>
    </div>
  );
};
