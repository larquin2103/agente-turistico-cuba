import { useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";
import type { Orientation } from "../../Video";
import { fontFamily } from "../../fonts";
import { visualBox } from "./_layout";

const steps = [
  { icon: "🛫", label: "Pre-viaje", sub: "Documentos · Visa · Pagos" },
  { icon: "🏨", label: "Check-in", sub: "Hotel · Traslado · Llegada" },
  { icon: "🗺", label: "Durante", sub: "Tours · Soporte · Dudas" },
  { icon: "💬", label: "Post-viaje", sub: "Encuesta · Próxima oferta" },
];

export const TravelTimeline: React.FC<{
  orientation: Orientation;
  color: string;
}> = ({ orientation, color }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <div style={visualBox(orientation)}>
      <div
        style={{
          width: "100%",
          maxWidth: 1000,
          margin: "0 auto",
        }}
      >
        {/* Line */}
        <div
          style={{
            position: "relative",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
            flexDirection: orientation === "portrait" ? "column" : "row",
            gap: orientation === "portrait" ? 18 : 0,
          }}
        >
          {/* Connector line */}
          {orientation !== "portrait" && (
            <div
              style={{
                position: "absolute",
                top: 36,
                left: "8%",
                right: "8%",
                height: 2,
                background: `linear-gradient(90deg, ${color}88, ${color}88)`,
                opacity: 0.4,
              }}
            />
          )}

          {steps.map((step, i) => {
            const stepSpring = spring({
              frame: frame - 12 - i * 20,
              fps,
              config: { damping: 12 },
            });
            const opacity = interpolate(stepSpring, [0, 1], [0, 1]);
            const scale = interpolate(stepSpring, [0, 1], [0.7, 1]);

            return (
              <div
                key={i}
                style={{
                  display: "flex",
                  flexDirection:
                    orientation === "portrait" ? "row" : "column",
                  alignItems: "center",
                  gap: orientation === "portrait" ? 16 : 10,
                  opacity,
                  transform: `scale(${scale})`,
                  zIndex: 2,
                  flex: orientation === "portrait" ? "0 0 auto" : 1,
                }}
              >
                <div
                  style={{
                    width: 72,
                    height: 72,
                    background: `${color}1a`,
                    border: `2px solid ${color}`,
                    borderRadius: "50%",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: 36,
                    boxShadow: `0 0 30px ${color}44`,
                    flexShrink: 0,
                  }}
                >
                  {step.icon}
                </div>
                <div
                  style={{
                    textAlign:
                      orientation === "portrait" ? "left" : "center",
                  }}
                >
                  <div
                    style={{
                      fontSize: 18,
                      color: "#f0ead8",
                      fontFamily: fontFamily.display,
                      fontWeight: 500,
                    }}
                  >
                    {step.label}
                  </div>
                  <div
                    style={{
                      fontSize: 12,
                      color: "#888",
                      marginTop: 4,
                      maxWidth: 140,
                    }}
                  >
                    {step.sub}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Bot presence indicator */}
        <div
          style={{
            marginTop: 30,
            background: `${color}10`,
            border: `1px solid ${color}55`,
            borderRadius: 12,
            padding: "14px 20px",
            display: "flex",
            alignItems: "center",
            gap: 14,
            opacity: interpolate(frame, [100, 130], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
          }}
        >
          <div style={{ fontSize: 28 }}>🤖</div>
          <div
            style={{
              fontSize: 16,
              color: "#f0ead8",
              fontFamily: fontFamily.body,
            }}
          >
            Tu agente está en{" "}
            <span style={{ color, fontWeight: 600 }}>cada etapa</span> — sin
            contratar más personal
          </div>
        </div>
      </div>
    </div>
  );
};
