import { useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";
import type { Orientation } from "../../Video";
import { fontFamily } from "../../fonts";
import { visualBox } from "./_layout";

export const PlatformCompare: React.FC<{
  orientation: Orientation;
  color: string;
}> = ({ orientation, color }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const leftSpring = spring({ frame, fps, config: { damping: 13 } });
  const rightSpring = spring({ frame: frame - 25, fps, config: { damping: 13 } });

  // Animated counter for 93%
  const percent = Math.floor(interpolate(frame, [40, 90], [0, 93], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  }));

  return (
    <div style={visualBox(orientation)}>
      <div
        style={{
          display: "flex",
          flexDirection: orientation === "portrait" ? "column" : "row",
          gap: 26,
          width: "100%",
          maxWidth: 1100,
          margin: "0 auto",
        }}
      >
        {/* Custom app — bad */}
        <div
          style={{
            flex: 1,
            background: "#160a0a",
            border: "1px solid #e05c5c44",
            borderRadius: 18,
            padding: 26,
            opacity: interpolate(leftSpring, [0, 1], [0, 1]),
            transform: `translateY(${interpolate(leftSpring, [0, 1], [30, 0])}px)`,
          }}
        >
          <div
            style={{
              fontFamily: fontFamily.mono,
              fontSize: 12,
              letterSpacing: 3,
              color: "#e05c5c",
              marginBottom: 12,
            }}
          >
            ✗ APP NUEVA
          </div>
          <div style={{ fontSize: 80, textAlign: "center", marginBottom: 6 }}>
            📵
          </div>
          <div
            style={{
              fontSize: 16,
              color: "#bbb",
              textAlign: "center",
              fontFamily: fontFamily.body,
              marginBottom: 14,
            }}
          >
            Nadie la descarga.
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            {[
              "Fricción para el usuario",
              "Curva de aprendizaje",
              "Bajas tasas de adopción",
            ].map((t, i) => (
              <div
                key={i}
                style={{
                  fontSize: 12,
                  color: "#aa6c6c",
                  fontFamily: fontFamily.body,
                  paddingLeft: 14,
                  position: "relative",
                }}
              >
                <span
                  style={{
                    position: "absolute",
                    left: 0,
                    color: "#e05c5c",
                  }}
                >
                  ✗
                </span>
                {t}
              </div>
            ))}
          </div>
        </div>

        {/* WhatsApp — good */}
        <div
          style={{
            flex: 1,
            background: "rgba(37,211,102,0.05)",
            border: "1px solid rgba(37,211,102,0.5)",
            borderRadius: 18,
            padding: 26,
            opacity: interpolate(rightSpring, [0, 1], [0, 1]),
            transform: `translateY(${interpolate(rightSpring, [0, 1], [30, 0])}px)`,
            position: "relative",
            overflow: "hidden",
          }}
        >
          <div
            style={{
              fontFamily: fontFamily.mono,
              fontSize: 12,
              letterSpacing: 3,
              color: "#25d366",
              marginBottom: 12,
            }}
          >
            ✓ WHATSAPP + TELEGRAM
          </div>

          {/* Big % counter */}
          <div
            style={{
              fontSize: orientation === "portrait" ? 80 : 100,
              fontFamily: fontFamily.mono,
              color: "#25d366",
              textAlign: "center",
              fontWeight: 700,
              lineHeight: 1,
              letterSpacing: -3,
              textShadow: "0 0 30px rgba(37,211,102,0.4)",
            }}
          >
            {percent}%
          </div>
          <div
            style={{
              fontSize: 14,
              color: "#a3e9c5",
              textAlign: "center",
              fontFamily: fontFamily.body,
              marginBottom: 16,
            }}
          >
            penetración en Latinoamérica
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            {[
              "Ya la tienen instalada",
              "Confían en la plataforma",
              "No descargan nada",
            ].map((t, i) => (
              <div
                key={i}
                style={{
                  fontSize: 13,
                  color: "#d4f0d8",
                  fontFamily: fontFamily.body,
                  paddingLeft: 16,
                  position: "relative",
                  opacity: interpolate(frame, [60 + i * 6, 75 + i * 6], [0, 1], {
                    extrapolateLeft: "clamp",
                    extrapolateRight: "clamp",
                  }),
                }}
              >
                <span
                  style={{
                    position: "absolute",
                    left: 0,
                    color: "#25d366",
                  }}
                >
                  ✓
                </span>
                {t}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
