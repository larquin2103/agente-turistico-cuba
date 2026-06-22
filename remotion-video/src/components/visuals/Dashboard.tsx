import { useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";
import type { Orientation } from "../../Video";
import { fontFamily } from "../../fonts";
import { visualBox } from "./_layout";

interface Metric {
  label: string;
  value: string;
  trend: "up" | "down-good";
}

export const Dashboard: React.FC<{
  orientation: Orientation;
  color: string;
  metrics: Metric[];
}> = ({ orientation, color, metrics }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Animated rising graph
  const graphProgress = interpolate(frame, [10, 90], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div style={visualBox(orientation)}>
      <div
        style={{
          background: "#0a0a0a",
          border: `1px solid ${color}44`,
          borderRadius: 18,
          padding: orientation === "portrait" ? 22 : 30,
          width: "100%",
          maxWidth: orientation === "portrait" ? 580 : 1000,
          margin: "0 auto",
          boxShadow: `0 0 40px ${color}22`,
        }}
      >
        {/* Dashboard header */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: 22,
            paddingBottom: 14,
            borderBottom: `1px solid ${color}22`,
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div
              style={{
                width: 10,
                height: 10,
                borderRadius: "50%",
                background: color,
                boxShadow: `0 0 10px ${color}`,
              }}
            />
            <div
              style={{
                fontSize: 16,
                color: "#f0ead8",
                fontFamily: fontFamily.body,
                fontWeight: 600,
              }}
            >
              Dashboard · Últimos 30 días
            </div>
          </div>
          <div
            style={{
              fontSize: 12,
              color: "#666",
              fontFamily: fontFamily.mono,
              letterSpacing: 2,
            }}
          >
            ● LIVE
          </div>
        </div>

        {/* Metrics grid */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns:
              orientation === "portrait"
                ? "1fr"
                : `repeat(${metrics.length}, 1fr)`,
            gap: 14,
            marginBottom: 22,
          }}
        >
          {metrics.map((m, i) => {
            const metricSpring = spring({
              frame: frame - 15 - i * 10,
              fps,
              config: { damping: 12 },
            });
            const scale = interpolate(metricSpring, [0, 1], [0.7, 1]);
            const opacity = interpolate(metricSpring, [0, 1], [0, 1]);

            return (
              <div
                key={i}
                style={{
                  background: `${color}0a`,
                  border: `1px solid ${color}33`,
                  borderRadius: 12,
                  padding: 18,
                  opacity,
                  transform: `scale(${scale})`,
                  transformOrigin: "left center",
                }}
              >
                <div
                  style={{
                    fontSize: 12,
                    color: "#888",
                    fontFamily: fontFamily.body,
                    marginBottom: 6,
                    letterSpacing: 0.3,
                  }}
                >
                  {m.label}
                </div>
                <div
                  style={{
                    fontSize: orientation === "portrait" ? 40 : 50,
                    color,
                    fontFamily: fontFamily.mono,
                    fontWeight: 700,
                    lineHeight: 1,
                    letterSpacing: -1,
                  }}
                >
                  {m.value}
                </div>
                <div
                  style={{
                    fontSize: 11,
                    color: m.trend === "up" ? "#4cc9a8" : "#4cc9a8",
                    marginTop: 4,
                    fontFamily: fontFamily.mono,
                  }}
                >
                  {m.trend === "up" ? "↗ Tendencia positiva" : "↘ Reducción"}
                </div>
              </div>
            );
          })}
        </div>

        {/* Mini graph */}
        <div
          style={{
            background: "#050505",
            borderRadius: 10,
            padding: 14,
          }}
        >
          <div
            style={{
              fontSize: 11,
              color: "#666",
              fontFamily: fontFamily.mono,
              letterSpacing: 2,
              marginBottom: 8,
            }}
          >
            EVOLUCIÓN MENSUAL
          </div>
          <svg
            viewBox="0 0 100 32"
            style={{
              width: "100%",
              height: orientation === "portrait" ? 70 : 90,
            }}
            preserveAspectRatio="none"
          >
            <defs>
              <linearGradient id="riseGrad" x1="0" x2="0" y1="0" y2="1">
                <stop offset="0%" stopColor={color} stopOpacity="0.5" />
                <stop offset="100%" stopColor={color} stopOpacity="0" />
              </linearGradient>
            </defs>
            {(() => {
              const points = Array.from({ length: 12 }).map((_, i) => ({
                x: i * 9,
                y: 28 - i * 1.8 - Math.sin(i * 1.2) * 1.5,
              }));
              const visible = points.slice(
                0,
                Math.ceil(points.length * graphProgress)
              );
              const lineD = visible
                .map((p, i) => `${i === 0 ? "M" : "L"} ${p.x} ${p.y}`)
                .join(" ");
              const areaD = visible.length
                ? `M 0 32 ${visible
                    .map((p) => `L ${p.x} ${p.y}`)
                    .join(" ")} L ${visible[visible.length - 1].x} 32 Z`
                : "";
              return (
                <>
                  <path d={areaD} fill="url(#riseGrad)" />
                  <path
                    d={lineD}
                    stroke={color}
                    strokeWidth="0.6"
                    fill="none"
                    strokeLinecap="round"
                  />
                  {visible.map((p, i) => (
                    <circle key={i} cx={p.x} cy={p.y} r="0.6" fill={color} />
                  ))}
                </>
              );
            })()}
          </svg>
        </div>
      </div>
    </div>
  );
};
