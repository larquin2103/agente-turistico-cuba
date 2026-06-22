import { useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";
import type { Orientation } from "../../Video";
import { fontFamily } from "../../fonts";
import { visualBox } from "./_layout";

const businesses = [
  { icon: "🩺", name: "Policlínico" },
  { icon: "🏥", name: "Hospital" },
  { icon: "🦷", name: "Consultorio Dental" },
  { icon: "💊", name: "Farmacia" },
  { icon: "🚑", name: "Urgencias" },
  { icon: "✈️", name: "Agencia de Viajes" },
  { icon: "🏨", name: "Hotel" },
  { icon: "🏠", name: "Casa Particular" },
  { icon: "🏛", name: "Centro Histórico" },
  { icon: "🏖", name: "Playa Santa Lucía" },
];

export const BusinessCarousel: React.FC<{
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
          maxWidth: 1100,
          margin: "0 auto",
          display: "grid",
          gridTemplateColumns:
            orientation === "portrait"
              ? "repeat(2, 1fr)"
              : "repeat(5, 1fr)",
          gap: 14,
        }}
      >
        {businesses.map((biz, i) => {
          const cardSpring = spring({
            frame: frame - 8 - i * 6,
            fps,
            config: { damping: 13 },
          });
          const opacity = interpolate(cardSpring, [0, 1], [0, 1]);
          const scale = interpolate(cardSpring, [0, 1], [0.7, 1]);

          return (
            <div
              key={i}
              style={{
                background: `${color}10`,
                border: `1px solid ${color}44`,
                borderRadius: 14,
                padding: orientation === "portrait" ? 16 : 20,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                gap: 8,
                opacity,
                transform: `scale(${scale})`,
              }}
            >
              <div
                style={{
                  fontSize: orientation === "portrait" ? 40 : 50,
                }}
              >
                {biz.icon}
              </div>
              <div
                style={{
                  fontSize: orientation === "portrait" ? 12 : 13,
                  color: "#f0ead8",
                  fontFamily: fontFamily.body,
                  textAlign: "center",
                  fontWeight: 500,
                  lineHeight: 1.2,
                }}
              >
                {biz.name}
              </div>
              <div
                style={{
                  fontSize: 16,
                  color,
                  marginTop: 2,
                }}
              >
                ✓
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
