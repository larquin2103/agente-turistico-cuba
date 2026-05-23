import { useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";
import type { Orientation } from "../../Video";
import { fontFamily } from "../../fonts";
import { visualBox } from "./_layout";

export const BeforeAfter: React.FC<{
  orientation: Orientation;
  color: string;
}> = ({ orientation, color }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const leftSpring = spring({ frame, fps, config: { damping: 14 } });
  const rightSpring = spring({ frame: frame - 25, fps, config: { damping: 14 } });

  const leftX = interpolate(leftSpring, [0, 1], [-60, 0]);
  const rightX = interpolate(rightSpring, [0, 1], [60, 0]);
  const leftOpacity = interpolate(leftSpring, [0, 1], [0, 1]);
  const rightOpacity = interpolate(rightSpring, [0, 1], [0, 1]);

  return (
    <div style={visualBox(orientation)}>
      <div
        style={{
          display: "flex",
          flexDirection: orientation === "portrait" ? "column" : "row",
          gap: 24,
          width: "100%",
          maxWidth: 1100,
          margin: "0 auto",
        }}
      >
        {/* ANTES */}
        <div
          style={{
            flex: 1,
            background: "#1a0a0a",
            border: "1px solid #e05c5c44",
            borderRadius: 18,
            padding: 26,
            opacity: leftOpacity,
            transform: `translateX(${leftX}px)`,
          }}
        >
          <div
            style={{
              fontFamily: fontFamily.mono,
              fontSize: 13,
              letterSpacing: 3,
              color: "#e05c5c",
              marginBottom: 14,
            }}
          >
            ◉ ANTES
          </div>
          <div
            style={{
              fontSize: 22,
              color: "#f0ead8",
              fontFamily: fontFamily.display,
              marginBottom: 18,
            }}
          >
            Caos manual
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {[
              { label: "Citas canceladas hoy", value: "3" },
              { label: "Llamadas sin respuesta", value: "8" },
              { label: "Recordatorios enviados", value: "0" },
            ].map((m, i) => (
              <div
                key={i}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  fontSize: 16,
                  color: "#bbb",
                  padding: "8px 12px",
                  background: "#240a0a",
                  borderRadius: 8,
                  fontFamily: fontFamily.body,
                  opacity: interpolate(frame, [15 + i * 5, 30 + i * 5], [0, 1], {
                    extrapolateLeft: "clamp",
                    extrapolateRight: "clamp",
                  }),
                }}
              >
                <span>{m.label}</span>
                <span
                  style={{
                    color: "#e05c5c",
                    fontFamily: fontFamily.mono,
                    fontWeight: 700,
                  }}
                >
                  {m.value}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Divider */}
        {orientation !== "portrait" && (
          <div
            style={{
              width: 2,
              background: `linear-gradient(180deg, transparent, ${color}88, transparent)`,
              alignSelf: "stretch",
            }}
          />
        )}

        {/* DESPUÉS */}
        <div
          style={{
            flex: 1,
            background: `${color}10`,
            border: `1px solid ${color}66`,
            borderRadius: 18,
            padding: 26,
            opacity: rightOpacity,
            transform: `translateX(${rightX}px)`,
          }}
        >
          <div
            style={{
              fontFamily: fontFamily.mono,
              fontSize: 13,
              letterSpacing: 3,
              color: color,
              marginBottom: 14,
            }}
          >
            ✦ DESPUÉS
          </div>
          <div
            style={{
              fontSize: 22,
              color: "#f0ead8",
              fontFamily: fontFamily.display,
              marginBottom: 18,
            }}
          >
            Automatizado
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {[
              { label: "Citas canceladas hoy", value: "0" },
              { label: "Recordatorios 24h antes", value: "12" },
              { label: "Recordatorios 2h antes", value: "12" },
              { label: "Confirmaciones automáticas", value: "11" },
            ].map((m, i) => (
              <div
                key={i}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  fontSize: 15,
                  color: "#bbb",
                  padding: "8px 12px",
                  background: `${color}0d`,
                  borderRadius: 8,
                  fontFamily: fontFamily.body,
                  opacity: interpolate(frame, [40 + i * 5, 55 + i * 5], [0, 1], {
                    extrapolateLeft: "clamp",
                    extrapolateRight: "clamp",
                  }),
                }}
              >
                <span>{m.label}</span>
                <span
                  style={{
                    color: color,
                    fontFamily: fontFamily.mono,
                    fontWeight: 700,
                  }}
                >
                  {m.value}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
