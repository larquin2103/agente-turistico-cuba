import { useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";
import type { Orientation } from "../../Video";
import { fontFamily } from "../../fonts";
import { visualBox } from "./_layout";

const steps = [
  { icon: "📄", title: "Subes", sub: "Servicios, horarios, protocolos" },
  { icon: "🧠", title: "Aprende", sub: "IA entrena en minutos" },
  { icon: "💬", title: "Responde", sub: "24/7 como tú lo harías" },
];

export const HowItWorks: React.FC<{
  orientation: Orientation;
  color: string;
}> = ({ orientation, color }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <div style={visualBox(orientation)}>
      <div
        style={{
          display: "flex",
          flexDirection: orientation === "portrait" ? "column" : "row",
          alignItems: "center",
          justifyContent: "center",
          gap: orientation === "portrait" ? 30 : 60,
          width: "100%",
        }}
      >
        {steps.map((step, i) => {
          const stepSpring = spring({
            frame: frame - 15 - i * 20,
            fps,
            config: { damping: 12 },
          });
          const stepScale = interpolate(stepSpring, [0, 1], [0.6, 1]);
          const stepOpacity = interpolate(stepSpring, [0, 1], [0, 1]);

          return (
            <div key={i} style={{ display: "contents" }}>
              <div
                style={{
                  width: orientation === "portrait" ? 240 : 260,
                  height: orientation === "portrait" ? 240 : 260,
                  background: `${color}10`,
                  border: `2px solid ${color}55`,
                  borderRadius: 24,
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: 12,
                  opacity: stepOpacity,
                  transform: `scale(${stepScale})`,
                  position: "relative",
                }}
              >
                {/* Step number */}
                <div
                  style={{
                    position: "absolute",
                    top: 14,
                    right: 18,
                    fontSize: 14,
                    fontFamily: fontFamily.mono,
                    color: `${color}aa`,
                    letterSpacing: 2,
                  }}
                >
                  0{i + 1}
                </div>
                <div style={{ fontSize: 64 }}>{step.icon}</div>
                <div
                  style={{
                    fontSize: 28,
                    color: "#f0ead8",
                    fontFamily: fontFamily.display,
                    fontWeight: 500,
                  }}
                >
                  {step.title}
                </div>
                <div
                  style={{
                    fontSize: 14,
                    color: "#999",
                    textAlign: "center",
                    padding: "0 18px",
                    fontFamily: fontFamily.body,
                  }}
                >
                  {step.sub}
                </div>
              </div>

              {/* Arrow */}
              {i < steps.length - 1 && (
                <div
                  style={{
                    fontSize: orientation === "portrait" ? 32 : 42,
                    color: `${color}66`,
                    opacity: interpolate(frame, [25 + i * 20, 40 + i * 20], [0, 1], {
                      extrapolateLeft: "clamp",
                      extrapolateRight: "clamp",
                    }),
                    transform:
                      orientation === "portrait" ? "rotate(90deg)" : "none",
                  }}
                >
                  →
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
