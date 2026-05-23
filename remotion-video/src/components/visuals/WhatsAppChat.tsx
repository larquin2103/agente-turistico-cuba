import { useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";
import type { Orientation } from "../../Video";
import { fontFamily } from "../../fonts";
import { visualBox } from "./_layout";

type ChatContext = "dental_midnight" | "travel_airport" | "travel_sale";

interface Message {
  from: "user" | "bot";
  text: string;
  typing?: boolean;
}

const conversations: Record<ChatContext, {
  header: string;
  subheader: string;
  messages: Message[];
}> = {
  dental_midnight: {
    header: "Clínica Dental Sonrisa",
    subheader: "● En línea · 00:12 AM",
    messages: [
      { from: "user", text: "Hola, tengo un dolor de muela horrible 😖 ¿Tienen cita urgente mañana?" },
      { from: "bot", text: "¡Hola! Lamento que estés con dolor. Sí, tenemos disponibilidad mañana:" },
      { from: "bot", text: "🕘 9:00 AM\n🕚 11:30 AM\n🕒 3:00 PM\n\nLa consulta de urgencia tiene un costo de $450. ¿Te reservo alguna?" },
      { from: "user", text: "Las 9 AM por favor 🙏" },
      { from: "bot", text: "✓ Listo. Cita confirmada mañana 9:00 AM con el Dr. Méndez. Te envío un recordatorio 1 hora antes." },
    ],
  },
  travel_airport: {
    header: "Viajes & Aventura",
    subheader: "● En línea · 02:14 AM",
    messages: [
      { from: "user", text: "Estoy en el aeropuerto, mi vuelo aterrizó. ¿A qué hora puedo hacer check-in en el hotel?" },
      { from: "bot", text: "¡Bienvenido a Cancún! Tu hotel (Riu Palace) acepta check-in temprano desde las 10:00 AM. Como tu vuelo llegó a las 2 AM, puedes:" },
      { from: "bot", text: "🛏 Usar el lobby + desayuno cortesía (incluido)\n🚕 El traslado privado te espera en la salida 4\n📞 Contacto del hotel: +52 998 881 8888" },
      { from: "user", text: "¡Perfecto, muchas gracias!" },
      { from: "bot", text: "Buen viaje 🌴 Cualquier cosa durante la estadía, aquí estoy 24/7." },
    ],
  },
  travel_sale: {
    header: "Viajes & Aventura",
    subheader: "● En línea · 22:43",
    messages: [
      { from: "user", text: "Hola, busco un paquete a Cancún para 4 personas en julio" },
      { from: "bot", text: "¡Excelente elección! Tengo 3 opciones disponibles:" },
      { from: "bot", text: "✈️ Riu Palace · 7 noches · $24,500/persona\n✈️ Iberostar Selection · 7 noches · $28,900/p\n✈️ Hard Rock Cancún · 7 noches · $32,400/p\n\nTodos con vuelo + traslados + desayunos. ¿Te envío detalles de alguno?" },
      { from: "user", text: "El Riu Palace me interesa, ¿confirmamos?" },
      { from: "bot", text: "✓ Reserva pre-confirmada. Te envío el link de pago seguro y el itinerario completo." },
    ],
  },
};

export const WhatsAppChat: React.FC<{
  orientation: Orientation;
  color: string;
  context: ChatContext;
}> = ({ orientation, context }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const convo = conversations[context];
  const phoneSpring = spring({
    frame: frame - 8,
    fps,
    config: { damping: 14 },
  });
  const phoneScale = interpolate(phoneSpring, [0, 1], [0.85, 1]);
  const phoneOpacity = interpolate(phoneSpring, [0, 1], [0, 1]);

  const phoneWidth = orientation === "portrait" ? 420 : 460;
  const phoneHeight = orientation === "portrait" ? 620 : 640;

  // Stagger messages
  const messageDelay = 30;
  const messageInterval = 38;

  return (
    <div style={visualBox(orientation)}>
      <div
        style={{
          width: phoneWidth,
          height: phoneHeight,
          background: "#0d0d0d",
          border: "6px solid #1a1a1a",
          borderRadius: 44,
          padding: 8,
          opacity: phoneOpacity,
          transform: `scale(${phoneScale})`,
          boxShadow: "0 0 60px rgba(37,211,102,0.15)",
          overflow: "hidden",
          fontFamily: fontFamily.body,
        }}
      >
        {/* WhatsApp header */}
        <div
          style={{
            background: "#075e54",
            padding: "14px 16px",
            borderRadius: "36px 36px 0 0",
            display: "flex",
            alignItems: "center",
            gap: 12,
          }}
        >
          <div style={{ color: "#fff", fontSize: 18 }}>←</div>
          <div
            style={{
              width: 36,
              height: 36,
              borderRadius: "50%",
              background: "#25d366",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 18,
            }}
          >
            🤖
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ color: "#fff", fontSize: 15, fontWeight: 600 }}>
              {convo.header}
            </div>
            <div style={{ color: "#a3e9c5", fontSize: 11 }}>
              {convo.subheader}
            </div>
          </div>
        </div>

        {/* Chat body */}
        <div
          style={{
            background:
              "#0b141a url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='100' height='100'><rect fill='%230b141a'/></svg>\")",
            height: phoneHeight - 80,
            padding: "12px 14px",
            overflow: "hidden",
            display: "flex",
            flexDirection: "column",
            gap: 8,
          }}
        >
          {convo.messages.map((msg, i) => {
            const appearFrame = messageDelay + i * messageInterval;
            const msgSpring = spring({
              frame: frame - appearFrame,
              fps,
              config: { damping: 13, stiffness: 140 },
            });
            const msgOpacity = interpolate(msgSpring, [0, 1], [0, 1]);
            const msgY = interpolate(msgSpring, [0, 1], [10, 0]);

            const isBot = msg.from === "bot";
            return (
              <div
                key={i}
                style={{
                  display: "flex",
                  justifyContent: isBot ? "flex-start" : "flex-end",
                  opacity: msgOpacity,
                  transform: `translateY(${msgY}px)`,
                }}
              >
                <div
                  style={{
                    background: isBot ? "#1f2c33" : "#005c4b",
                    color: "#e9edef",
                    fontSize: 13,
                    lineHeight: 1.4,
                    padding: "8px 11px",
                    borderRadius: 8,
                    maxWidth: "78%",
                    whiteSpace: "pre-line",
                    boxShadow: "0 1px 1px rgba(0,0,0,0.13)",
                    borderTopLeftRadius: isBot ? 2 : 8,
                    borderTopRightRadius: isBot ? 8 : 2,
                  }}
                >
                  {msg.text}
                  <div
                    style={{
                      fontSize: 9,
                      color: "#8696a0",
                      textAlign: "right",
                      marginTop: 2,
                      letterSpacing: 0.5,
                    }}
                  >
                    {String(Math.floor(appearFrame / 30) + 12).padStart(2, "0")}:
                    {String((appearFrame % 30) * 2).padStart(2, "0")}
                    {!isBot && (
                      <span style={{ color: "#53bdeb", marginLeft: 4 }}>✓✓</span>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
