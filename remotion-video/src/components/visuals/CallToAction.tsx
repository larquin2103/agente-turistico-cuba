import { useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";
import type { Orientation } from "../../Video";
import { fontFamily } from "../../fonts";
import { visualBox } from "./_layout";

export const CallToAction: React.FC<{
  orientation: Orientation;
  color: string;
}> = ({ orientation }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const ctaSpring = spring({ frame: frame - 10, fps, config: { damping: 12 } });
  const qrSpring = spring({ frame: frame - 30, fps, config: { damping: 13 } });

  const pulse = 1 + Math.sin(frame * 0.15) * 0.04;

  return (
    <div style={visualBox(orientation)}>
      <div
        style={{
          width: "100%",
          maxWidth: 900,
          margin: "0 auto",
          display: "flex",
          flexDirection: orientation === "portrait" ? "column" : "row",
          alignItems: "center",
          gap: 40,
        }}
      >
        {/* CTA Button + phone */}
        <div
          style={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            gap: 16,
            opacity: interpolate(ctaSpring, [0, 1], [0, 1]),
            transform: `scale(${interpolate(ctaSpring, [0, 1], [0.8, 1])})`,
          }}
        >
          <div
            style={{
              fontSize: 12,
              color: "#888",
              fontFamily: fontFamily.mono,
              letterSpacing: 4,
              textTransform: "uppercase",
            }}
          >
            ✦ Demo gratuita
          </div>

          <div
            style={{
              background: "#25d366",
              color: "#000",
              padding: "20px 28px",
              borderRadius: 18,
              fontSize: orientation === "portrait" ? 26 : 32,
              fontFamily: fontFamily.body,
              fontWeight: 700,
              display: "flex",
              alignItems: "center",
              gap: 14,
              transform: `scale(${pulse})`,
              boxShadow: "0 0 40px rgba(37,211,102,0.4)",
            }}
          >
            <span style={{ fontSize: 36 }}>💬</span>
            <span>+52 55 1234 5678</span>
          </div>

          <div
            style={{
              fontSize: 18,
              color: "#f0ead8",
              fontFamily: fontFamily.display,
              fontStyle: "italic",
              marginTop: 8,
            }}
          >
            “Tu agente listo en 15 minutos.”
          </div>

          <div
            style={{
              display: "flex",
              gap: 10,
              marginTop: 12,
              flexWrap: "wrap",
            }}
          >
            {["Sin contratos", "Operativo hoy", "Setup en 15 min"].map((t, i) => (
              <div
                key={i}
                style={{
                  background: "rgba(255,255,255,0.05)",
                  border: "1px solid rgba(255,255,255,0.1)",
                  borderRadius: 999,
                  padding: "6px 14px",
                  fontSize: 13,
                  color: "#ccc",
                  fontFamily: fontFamily.body,
                }}
              >
                ✓ {t}
              </div>
            ))}
          </div>
        </div>

        {/* QR Code */}
        <div
          style={{
            background: "#fff",
            padding: 18,
            borderRadius: 16,
            opacity: interpolate(qrSpring, [0, 1], [0, 1]),
            transform: `scale(${interpolate(qrSpring, [0, 1], [0.7, 1])})`,
            boxShadow: "0 0 50px rgba(255,255,255,0.1)",
          }}
        >
          <FakeQR size={orientation === "portrait" ? 180 : 220} />
          <div
            style={{
              fontSize: 11,
              color: "#000",
              textAlign: "center",
              marginTop: 8,
              fontFamily: fontFamily.mono,
              letterSpacing: 2,
            }}
          >
            ESCANÉAME
          </div>
        </div>
      </div>
    </div>
  );
};

// Decorative QR (not a real code — for the visual)
const FakeQR: React.FC<{ size: number }> = ({ size }) => {
  const grid = 21;
  // deterministic pattern
  const cells: boolean[] = Array.from({ length: grid * grid }).map((_, i) => {
    return ((i * 17 + Math.floor(i / grid) * 31) % 7) % 3 === 0;
  });

  return (
    <svg
      width={size}
      height={size}
      viewBox={`0 0 ${grid} ${grid}`}
      style={{ display: "block" }}
    >
      <rect width={grid} height={grid} fill="#fff" />
      {cells.map((on, i) => {
        if (!on) return null;
        const x = i % grid;
        const y = Math.floor(i / grid);
        // Reserve corners for finder patterns
        const inFinder =
          (x < 7 && y < 7) ||
          (x > grid - 8 && y < 7) ||
          (x < 7 && y > grid - 8);
        if (inFinder) return null;
        return <rect key={i} x={x} y={y} width="1" height="1" fill="#000" />;
      })}
      {/* Finder patterns */}
      {[
        [0, 0],
        [grid - 7, 0],
        [0, grid - 7],
      ].map(([fx, fy], idx) => (
        <g key={idx}>
          <rect x={fx} y={fy} width="7" height="7" fill="#000" />
          <rect x={fx + 1} y={fy + 1} width="5" height="5" fill="#fff" />
          <rect x={fx + 2} y={fy + 2} width="3" height="3" fill="#000" />
        </g>
      ))}
    </svg>
  );
};
