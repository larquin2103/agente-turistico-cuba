export type ActKey =
  | "INTRO"
  | "SOLUCION"
  | "CLINICA_DENTAL"
  | "TURISMO"
  | "VENTAJAS"
  | "CIERRE";

export interface Scene {
  id: number;
  act: ActKey;
  actLabel: string;
  time: string;
  duration: number;
  title: string;
  visual: string;
  narration: string;
  stat: string | null;
  hook: string | null;
  color: string;
  bg: string;
}

export const FPS = 30;

export const actMeta: Record<
  ActKey,
  { badge: string; text: string; emoji: string }
> = {
  INTRO: { badge: "#e05c5c", text: "INTRO", emoji: "🔴" },
  SOLUCION: { badge: "#4c9ac9", text: "SOLUCIÓN", emoji: "💡" },
  CLINICA_DENTAL: {
    badge: "#c94c7a",
    text: "SALUD",
    emoji: "🩺",
  },
  TURISMO: { badge: "#4c7ac9", text: "TURISMO", emoji: "✈️" },
  VENTAJAS: { badge: "#c9a84c", text: "VENTAJAS", emoji: "⚡" },
  CIERRE: { badge: "#a84cc9", text: "CIERRE", emoji: "🎯" },
};

type RawScene = Omit<Scene, "time">;

const rawScenes: RawScene[] = [
  {
    id: 1,
    act: "INTRO",
    actLabel: "INTRO",
    duration: 12,
    title: "El problema que frena la atención",
    visual:
      "Pantalla negra. Teléfono sonando a las 11:30 PM. Nadie contesta. Tres mensajes de WhatsApp sin respuesta con ticks grises.",
    narration:
      "Son las 11 de la noche. En Camagüey, una persona necesita orientación… pero del otro lado no hay nadie. Y esa oportunidad de ayudar se pierde.",
    stat: null,
    hook: "El 67% de las personas abandona cuando nadie responde a tiempo.",
    color: "#c9a84c",
    bg: "#0a0a0a",
  },
  {
    id: 2,
    act: "INTRO",
    actLabel: "INTRO",
    duration: 11,
    title: "Lo que se erosiona sin respuesta",
    visual:
      "Contadores en rojo: llamadas perdidas, mensajes sin responder, citas canceladas. Gráfica de atención al usuario bajando.",
    narration:
      "Cada mensaje sin responder es un usuario sin orientar, una cita perdida, un servicio que se erosiona. Y un territorio que avanza más lento.",
    stat: "1 de cada 3 cancelaciones ocurre porque nadie confirmó la cita a tiempo.",
    hook: null,
    color: "#e05c5c",
    bg: "#0f0a0a",
  },
  {
    id: 3,
    act: "SOLUCION",
    actLabel: "SOLUCIÓN",
    duration: 14,
    title: "Una herramienta para la transformación digital",
    visual:
      "Transición a azul brillante. Logo del producto. WhatsApp y Telegram abiertos. Respuesta instantánea en 2 segundos.",
    narration:
      "Presentamos tu Agente Inteligente 24/7: una herramienta que aporta a la Transformación Digital Inteligente de Camagüey, al servicio de la salud y el turismo.",
    stat: null,
    hook: "Responde en WhatsApp y Telegram. Sin apps. Sin barreras.",
    color: "#4c9ac9",
    bg: "#03080f",
  },
  {
    id: 4,
    act: "SOLUCION",
    actLabel: "SOLUCIÓN",
    duration: 12,
    title: "Cómo funciona",
    visual:
      "Animación: documentos entrando a una caja → cerebro con IA → burbuja de chat respondiendo.",
    narration:
      "Cargas tu información: servicios, horarios, orientaciones y protocolos. La IA los aprende en minutos y responde como tú lo harías. Sin saber programar.",
    stat: "Configuración en menos de 15 minutos. Tecnología avanzada, uso simple.",
    hook: null,
    color: "#4cc9a8",
    bg: "#030f0c",
  },
  {
    id: 5,
    act: "CLINICA_DENTAL",
    actLabel: "SALUD",
    duration: 14,
    title: "Orientación a medianoche",
    visual:
      "Consulta dental, 00:12 AM. Un paciente con una urgencia escribe por WhatsApp. El agente responde al instante con orientación y horarios.",
    narration:
      "Tu paciente tiene una urgencia a medianoche. El agente le responde de inmediato, lo orienta y lo tranquiliza. Asistencia 24/7, incluso fuera de horario.",
    stat: null,
    hook: "El paciente recibe orientación al instante. Y su consulta queda agendada.",
    color: "#c94c7a",
    bg: "#0f030a",
  },
  {
    id: 6,
    act: "CLINICA_DENTAL",
    actLabel: "SALUD",
    duration: 14,
    title: "Citas confirmadas, cero cancelaciones",
    visual:
      "Pantalla dividida: ANTES (citas canceladas) / DESPUÉS (agente enviando recordatorios automáticos).",
    narration:
      "El agente recuerda la cita 24 y 2 horas antes. Si el paciente no puede, reagenda al momento. Menos cancelaciones y mejor aprovechamiento de cada consulta.",
    stat: "Las instituciones con recordatorios automáticos reducen cancelaciones hasta un 70%.",
    hook: null,
    color: "#c94c7a",
    bg: "#0f030a",
  },
  {
    id: 7,
    act: "CLINICA_DENTAL",
    actLabel: "SALUD",
    duration: 14,
    title: "Libera el tiempo de tu equipo",
    visual:
      "Personal de salud agotado respondiendo lo mismo. Corte: el agente responde horarios, indicaciones y orientaciones.",
    narration:
      "Horarios, indicaciones, requisitos, orientaciones… Tu equipo deja de repetir lo mismo decenas de veces al día y se enfoca en lo que importa: atender a las personas.",
    stat: "Tu equipo recupera 3-4 horas al día para la atención presencial.",
    hook: null,
    color: "#c94c7a",
    bg: "#0f030a",
  },
  {
    id: 8,
    act: "CLINICA_DENTAL",
    actLabel: "SALUD",
    duration: 12,
    title: "Un servicio de salud que se fortalece",
    visual:
      "Dashboard: +40% citas confirmadas, -65% cancelaciones, 0 mensajes sin responder. Personal de salud satisfecho.",
    narration:
      "Más personas orientadas, menos cancelaciones, pacientes que se sienten atendidos. Un servicio de salud que se fortalece y aporta al desarrollo del territorio.",
    stat: "+40% citas confirmadas · -65% cancelaciones · 0 mensajes sin responder",
    hook: null,
    color: "#c94c7a",
    bg: "#0f030a",
  },
  {
    id: 9,
    act: "TURISMO",
    actLabel: "TURISMO",
    duration: 14,
    title: "El viajero recién llegado",
    visual:
      "Aeropuerto, 2 AM. Un viajero confundido escribe a la agencia. El agente responde al instante con los detalles de su estancia en Camagüey.",
    narration:
      "Tu visitante llega a Camagüey a las 2 de la mañana. El agente ya está ahí: respondiendo, guiando, tranquilizando. Asistencia en el momento exacto.",
    stat: null,
    hook: "La llegada genera 4-6 preguntas urgentes. Casi siempre fuera de horario.",
    color: "#4c7ac9",
    bg: "#030a0f",
  },
  {
    id: 10,
    act: "TURISMO",
    actLabel: "TURISMO",
    duration: 14,
    title: "Atiende cuando otros no pueden",
    visual:
      "Familia consultando un paquete a Playa Santa Lucía a las 10 PM. El agente responde y confirma la reserva.",
    narration:
      "Cuando nadie más responde, tu agente orienta, confirma reservas y no deja escapar al visitante. El turismo de Camagüey atiende a toda hora.",
    stat: "El 58% de las consultas de viaje ocurren fuera del horario de oficina.",
    hook: null,
    color: "#4c7ac9",
    bg: "#030a0f",
  },
  {
    id: 11,
    act: "TURISMO",
    actLabel: "TURISMO",
    duration: 13,
    title: "Acompañamiento que genera reputación",
    visual:
      "Línea de tiempo: reserva → documentos → llegada → preguntas en destino → post-viaje. El agente presente en cada etapa.",
    narration:
      "Antes, durante y después del viaje, el agente acompaña en cada etapa. El visitante se siente cuidado y regresa. Así se construye la reputación de un destino.",
    stat: "El visitante se siente acompañado — sin contratar más personal.",
    hook: null,
    color: "#4c7ac9",
    bg: "#030a0f",
  },
  {
    id: 12,
    act: "TURISMO",
    actLabel: "TURISMO",
    duration: 12,
    title: "Visitantes satisfechos, destino fuerte",
    visual:
      "Dashboard: +55% reservas confirmadas, 100% mensajes respondidos, 4.9★ satisfacción.",
    narration:
      "Más reservas, mejor experiencia, visitantes que regresan y recomiendan. Cada visitante satisfecho fortalece el turismo del territorio.",
    stat: "+55% reservas confirmadas · 100% mensajes respondidos · 4.9★ satisfacción",
    hook: null,
    color: "#4c7ac9",
    bg: "#030a0f",
  },
  {
    id: 13,
    act: "VENTAJAS",
    actLabel: "VENTAJAS",
    duration: 13,
    title: "Tecnología inclusiva: WhatsApp y Telegram",
    visual:
      "Comparativa: app nueva (nadie la descarga) vs WhatsApp (todos la tienen y la usan a diario).",
    narration:
      "No le pides a nadie que descargue una app nueva. Le escribes por donde ya te escribe. Tecnología inclusiva, que llega a todos.",
    stat: "WhatsApp y Telegram: las apps que la gente ya usa todos los días.",
    hook: null,
    color: "#c9a84c",
    bg: "#0f0d03",
  },
  {
    id: 14,
    act: "VENTAJAS",
    actLabel: "VENTAJAS",
    duration: 12,
    title: "Confianza, no confusión",
    visual:
      "El agente responde SOLO con información oficial. 'No tengo esa información, te pongo en contacto con un asesor.'",
    narration:
      "El agente no improvisa. Solo responde con tu información oficial. Si no lo sabe, lo dice y conecta con tu equipo. Tecnología confiable.",
    stat: "Cero respuestas inventadas · Cero datos incorrectos · Cero malentendidos.",
    hook: null,
    color: "#c9a84c",
    bg: "#0f0d03",
  },
  {
    id: 15,
    act: "VENTAJAS",
    actLabel: "VENTAJAS",
    duration: 13,
    title: "Atiende a 10 o a 500 igual de bien",
    visual:
      "Un agente → 10 conversaciones. El mismo agente → 500 conversaciones simultáneas. Sin contratar más gente.",
    narration:
      "¿10 personas o 500? El agente responde a todas con la misma calidad y velocidad. El servicio más pequeño atiende como el más grande.",
    stat: "Maneja cientos de conversaciones simultáneas con la misma velocidad.",
    hook: null,
    color: "#c9a84c",
    bg: "#0f0d03",
  },
  {
    id: 16,
    act: "CIERRE",
    actLabel: "CIERRE",
    duration: 12,
    title: "Indispensable para la salud y el turismo",
    visual:
      "Mosaico de íconos de salud y turismo de Camagüey: policlínico, hospital, consultorio dental, farmacia, agencia de viajes, hotel, casa particular, centro histórico, Playa Santa Lucía.",
    narration:
      "Sin estas herramientas, la orientación se pierde y el servicio se erosiona. Con ellas, la salud y el turismo de Camagüey avanzan en su transformación digital.",
    stat: null,
    hook: "La transformación digital inteligente ya no es opcional. Es indispensable.",
    color: "#a84cc9",
    bg: "#0a030f",
  },
  {
    id: 17,
    act: "CIERRE",
    actLabel: "CIERRE",
    duration: 13,
    title: "Prueba la demo en vivo",
    visual:
      "Fondo negro elegante. Enlace de la demo grande y centrado: dentbotsonrisa.netlify.app. 'Tu agente listo en 15 minutos.'",
    narration:
      "Descubre cómo la inteligencia artificial contribuye a la salud y el turismo de Camagüey. Prueba la demo ahora mismo.",
    stat: null,
    hook: "Demo en vivo · Sin contratos · Operativo hoy mismo",
    color: "#ffffff",
    bg: "#050505",
  },
];

const fmt = (totalSec: number): string => {
  const m = Math.floor(totalSec / 60);
  const s = totalSec % 60;
  return `${m}:${String(s).padStart(2, "0")}`;
};

// Calcula el rango de tiempo de cada escena a partir de su duración
let _acc = 0;
export const scenes: Scene[] = rawScenes.map((s) => {
  const start = _acc;
  const end = _acc + s.duration;
  _acc = end;
  return { ...s, time: `${fmt(start)} – ${fmt(end)}` };
});

export const totalDurationSeconds = scenes.reduce(
  (acc, s) => acc + s.duration,
  0
);
export const totalDurationFrames = totalDurationSeconds * FPS;

// Devuelve el frame de inicio de cada escena
export const sceneStartFrames = scenes.reduce<number[]>((acc, s, i) => {
  const prev = acc[i - 1] ?? 0;
  const prevDuration = i === 0 ? 0 : scenes[i - 1].duration * FPS;
  acc.push(prev + prevDuration);
  return acc;
}, []);
