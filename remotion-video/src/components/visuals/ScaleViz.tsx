import { useCurrentFrame, interpolate } from "remotion";
import type { Orientation } from "../../Video";
import { fontFamily } from "../../fonts";
import { visualBox } from "./_layout";

export const ScaleViz: React.FC<{
  orientation: Orientation;
  color: string;
}> = ({ orientation, color }) => {
  const frame = useCurrentFrame();

  // Animated counter from 10 to 500
  const count = Math.floor(
    interpolate(frame, [20, 100], [10, 500], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    })
  );

  // Grid of dots representing conversations
  const dotsToShow = Math.floor((count / 500) * 100);

  return (
    <div style={visualBox(orientation)}>
      <div
        style={{
          width: "100%",
          maxWidth: 1000,
          margin: "0 auto",
          display: "flex",
          flexDirection: orientation === "portrait" ? "column" : "row",
          gap: 30,
          alignItems: "center",
        }}
      >
        {/* Bot center */}
        <div
          style={{
            position: "relative",
            width: orientation === "portrait" ? 180 : 220,
            height: orientation === "portrait" ? 180 : 220,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexShrink: 0,
          }}
        >
          {/* Ripple rings */}
          {[0, 1, 2].map((i) => {
            const rippleFrame = (frame + i * 20) % 60;
            const rippleScale = interpolate(rippleFrame, [0, 60], [0.5, 2]);
            const rippleOpacity = interpolate(rippleFrame, [0, 60], [0.6, 0]);
            return (
              <div
                key={i}
                style={{
                  position: "absolute",
                  inset: 0,
                  borderRadius: "50%",
                  border: `2px solid ${color}`,
                  transform: `scale(${rippleScale})`,
                  opacity: rippleOpacity,
                }}
              />
            );
          })}
          <div
            style={{
              width: "70%",
              height: "70%",
              borderRadius: "50%",
              background: `linear-gradient(135deg, ${color} 0%, ${color}aa 100%)`,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: orientation === "portrait" ? 60 : 80,
              boxShadow: `0 0 50px ${color}aa`,
            }}
          >
            🤖
          </div>
        </div>

        {/* Counter + dots */}
        <div style={{ flex: 1 }}>
          <div
            style={{
              fontSize: 14,
              color: "#888",
              fontFamily: fontFamily.mono,
              letterSpacing: 3,
              textTransform: "uppercase",
              marginBottom: 8,
            }}
          >
            Conversaciones simultáneas
          </div>
          <div
            style={{
              display: "flex",
              alignItems: "baseline",
              gap: 12,
              marginBottom: 18,
            }}
          >
            <div
              style={{
                fontSize: orientation === "portrait" ? 80 : 120,
                fontFamily: fontFamily.mono,
                color,
                fontWeight: 700,
                lineHeight: 1,
                letterSpacing: -3,
                textShadow: `0 0 30px ${color}88`,
              }}
            >
              {count}
            </div>
            <div
              style={{
                fontSize: 18,
                color: "#888",
                fontFamily: fontFamily.body,
              }}
            >
              al mismo tiempo
            </div>
          </div>

          {/* Dots grid */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(20, 1fr)",
              gap: 4,
              maxWidth: 480,
            }}
          >
            {Array.from({ length: 100 }).map((_, i) => (
              <div
                key={i}
                style={{
                  width: 14,
                  height: 14,
                  borderRadius: "50%",
                  background:
                    i < dotsToShow ? color : "rgba(255,255,255,0.05)",
                  transition: "background 100ms",
                  boxShadow: i < dotsToShow ? `0 0 4px ${color}` : "none",
                }}
              />
            ))}
          </div>

          <div
            style={{
              fontSize: 13,
              color: "#888",
              marginTop: 14,
              fontFamily: fontFamily.body,
            }}
          >
            Misma velocidad · Misma calidad · Sin contratar personal
          </div>
        </div>
      </div>
    </div>
  );
};
