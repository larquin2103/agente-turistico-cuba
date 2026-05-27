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
    text: "CLÍNICA DENTAL",
    emoji: "🦷",
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
    duration: 9,
    title: "El problema que frena a tu territorio",
    visual:
      "Pantalla negra. Teléfono sonando a las 11:30 PM. Nadie contesta. Tres mensajes de WhatsApp sin respuesta con ticks grises.",
    narration:
      "Son las 11 de la noche. En tu comunidad, un cliente está listo para comprar… pero nadie responde. Y esa oportunidad no vuelve.",
    stat: null,
    hook: "El 67% de los clientes elige al competidor que responde primero.",
    color: "#c9a84c",
    bg: "#0a0a0a",
  },
  {
    id: 2,
    act: "INTRO",
    actLabel: "INTRO",
    duration: 8,
    title: "La oportunidad perdida (en números)",
    visual:
      "Contador en rojo: llamadas perdidas, mensajes sin responder, citas canceladas. Gráfica de ingresos bajando.",
    narration:
      "Cada mensaje sin responder es una venta que tu negocio —y tu territorio— deja escapar. Una cita perdida. Un cliente que no vuelve.",
    stat: "1 de cada 3 cancelaciones ocurre porque nadie confirmó la cita a tiempo.",
    hook: null,
    color: "#e05c5c",
    bg: "#0f0a0a",
  },
  {
    id: 3,
    act: "SOLUCION",
    actLabel: "SOLUCIÓN",
    duration: 9,
    title: "Inteligencia artificial al alcance de todos",
    visual:
      "Transición a azul brillante. Logo del producto. WhatsApp y Telegram abiertos. Respuesta instantánea en 2 segundos.",
    narration:
      "Presentamos tu Agente Inteligente 24/7: tecnología de punta al alcance de cualquier negocio de tu región, que conoce tu negocio mejor que nadie.",
    stat: null,
    hook: "Responde en WhatsApp y Telegram. Sin apps. Sin barreras.",
    color: "#4c9ac9",
    bg: "#03080f",
  },
  {
    id: 4,
    act: "SOLUCION",
    actLabel: "SOLUCIÓN",
    duration: 9,
    title: "Cómo funciona",
    visual:
      "Animación: documentos PDF entrando a una caja → cerebro con IA → burbuja de chat respondiendo.",
    narration:
      "Subes tus precios, servicios y políticas. La IA los aprende en minutos y responde como tú lo harías. Sin saber programar nada.",
    stat: "Configuración en menos de 15 minutos. Tecnología avanzada, uso simple.",
    hook: null,
    color: "#4cc9a8",
    bg: "#030f0c",
  },
  {
    id: 5,
    act: "CLINICA_DENTAL",
    actLabel: "CLÍNICA DENTAL",
    duration: 12,
    title: "Paciente a medianoche",
    visual:
      "Persona con dolor de muela a las 12 AM escribe en WhatsApp. El agente responde en 2 segundos con horarios y precio.",
    narration:
      "Tu paciente tiene dolor a medianoche. El agente le responde de inmediato, le da opciones de cita y lo tranquiliza. Eso es satisfacción real.",
    stat: null,
    hook: "El paciente duerme tranquilo. Y la cita ya está agendada.",
    color: "#c94c7a",
    bg: "#0f030a",
  },
  {
    id: 6,
    act: "CLINICA_DENTAL",
    actLabel: "CLÍNICA DENTAL",
    duration: 12,
    title: "Citas confirmadas = cero cancelaciones",
    visual:
      "Pantalla dividida: ANTES (citas canceladas) / DESPUÉS (agente enviando recordatorios automáticos).",
    narration:
      "El agente recuerda la cita 24 y 2 horas antes. Si el paciente no puede, reagenda al momento. Menos cancelaciones y más confianza en tu servicio.",
    stat: "Las clínicas con recordatorios automáticos reducen cancelaciones hasta un 70%.",
    hook: null,
    color: "#c94c7a",
    bg: "#0f030a",
  },
  {
    id: 7,
    act: "CLINICA_DENTAL",
    actLabel: "CLÍNICA DENTAL",
    duration: 12,
    title: "Libera el tiempo de tu equipo",
    visual:
      "Asistente real agotada respondiendo lo mismo. Corte: el agente responde — precios, horarios, formas de pago.",
    narration:
      "Precios, horarios, formas de pago… Tu equipo deja de repetir lo mismo 30 veces al día y se enfoca en lo que importa: atender mejor a las personas.",
    stat: "Tu equipo recupera 3-4 horas al día para pacientes presenciales.",
    hook: null,
    color: "#c94c7a",
    bg: "#0f030a",
  },
  {
    id: 8,
    act: "CLINICA_DENTAL",
    actLabel: "CLÍNICA DENTAL",
    duration: 9,
    title: "Un negocio local que crece",
    visual:
      "Dashboard: +40% citas, -65% cancelaciones, 0 llamadas perdidas. Dentista sonriendo.",
    narration:
      "Más citas, menos cancelaciones, pacientes que se sienten atendidos. Un negocio local que crece y da mejor servicio a su comunidad.",
    stat: "+40% citas · -65% cancelaciones · 0 llamadas sin respuesta",
    hook: null,
    color: "#c94c7a",
    bg: "#0f030a",
  },
  {
    id: 9,
    act: "TURISMO",
    actLabel: "TURISMO",
    duration: 12,
    title: "El viajero perdido en el check-in",
    visual:
      "Aeropuerto, 2 AM. Viajero confundido escribe a la agencia. El agente responde al instante con todos los detalles del hotel.",
    narration:
      "Tu cliente está en el aeropuerto a las 2 de la mañana. El agente ya está ahí: respondiendo, guiando, tranquilizando. Satisfacción en el momento exacto.",
    stat: null,
    hook: "El check-in promedio genera 4-6 preguntas urgentes. Fuera de horario.",
    color: "#4c7ac9",
    bg: "#030a0f",
  },
  {
    id: 10,
    act: "TURISMO",
    actLabel: "TURISMO",
    duration: 12,
    title: "Compite de igual a igual",
    visual:
      "Familia navegando paquetes a las 10 PM. Preguntan por Cancún. El agente cierra la venta.",
    narration:
      "Cuando la competencia duerme, tu agente cierra ventas y confirma reservas. Tu negocio compite de igual a igual, sin importar su tamaño.",
    stat: "El 58% de las consultas de viaje ocurren fuera del horario de oficina.",
    hook: null,
    color: "#4c7ac9",
    bg: "#030a0f",
  },
  {
    id: 11,
    act: "TURISMO",
    actLabel: "TURISMO",
    duration: 11,
    title: "Acompañamiento que genera reputación",
    visual:
      "Timeline: reserva → documentos → check-in → preguntas en destino → post-viaje. El agente presente en cada etapa.",
    narration:
      "Antes, durante y después del viaje, el agente acompaña en cada etapa. El cliente se siente cuidado y vuelve. Así se construye reputación en tu territorio.",
    stat: "El cliente se siente acompañado — sin contratar más personal.",
    hook: null,
    color: "#4c7ac9",
    bg: "#030a0f",
  },
  {
    id: 12,
    act: "TURISMO",
    actLabel: "TURISMO",
    duration: 9,
    title: "Clientes satisfechos, comunidad fuerte",
    visual:
      "Dashboard: +55% conversión, 100% mensajes respondidos, 4.9★ satisfacción.",
    narration:
      "Más ventas, mejor experiencia, clientes que regresan y recomiendan. Cada negocio satisfecho fortalece la economía de su comunidad.",
    stat: "+55% conversión · 100% mensajes respondidos · 4.9★ satisfacción",
    hook: null,
    color: "#4c7ac9",
    bg: "#030a0f",
  },
  {
    id: 13,
    act: "VENTAJAS",
    actLabel: "VENTAJAS",
    duration: 11,
    title: "IA inclusiva: WhatsApp y Telegram",
    visual:
      "Comparativa: App nueva (nadie la descarga) vs WhatsApp (todos la tienen). 93% de penetración en Latinoamérica.",
    narration:
      "No le pides a nadie que descargue una app nueva. Le escribes por donde ya te escribe. Inteligencia artificial inclusiva, que llega a todos en tu región.",
    stat: "93% de penetración de WhatsApp en Latinoamérica.",
    hook: null,
    color: "#c9a84c",
    bg: "#0f0d03",
  },
  {
    id: 14,
    act: "VENTAJAS",
    actLabel: "VENTAJAS",
    duration: 9,
    title: "Confianza, no confusión",
    visual:
      "El agente responde SOLO con información de la empresa. 'No tengo esa información, te pongo en contacto con un asesor.'",
    narration:
      "El agente no improvisa. Solo responde con tu información. Si no lo sabe, lo dice y conecta con tu equipo. IA confiable para tu negocio.",
    stat: "Cero respuestas inventadas · Cero precios incorrectos · Cero malentendidos.",
    hook: null,
    color: "#c9a84c",
    bg: "#0f0d03",
  },
  {
    id: 15,
    act: "VENTAJAS",
    actLabel: "VENTAJAS",
    duration: 10,
    title: "El pequeño negocio atiende como uno grande",
    visual:
      "Un bot → 10 conversaciones. Mismo bot → 500 conversaciones simultáneas. Sin contratar más gente.",
    narration:
      "¿10 clientes o 500? El agente responde a todos con la misma calidad y velocidad. El pequeño negocio de tu barrio atiende como uno grande.",
    stat: "Maneja 500 conversaciones simultáneas con la misma velocidad.",
    hook: null,
    color: "#c9a84c",
    bg: "#0f0d03",
  },
  {
    id: 16,
    act: "CIERRE",
    actLabel: "CIERRE",
    duration: 9,
    title: "IA para cada negocio de tu territorio",
    visual:
      "Carrusel: clínica dental · agencia de turismo · restaurante · inmobiliaria · academia · spa · tienda · consultorio.",
    narration:
      "Clínicas, agencias, restaurantes, tiendas… Cuando cada negocio de tu comunidad adopta IA, todo el territorio crece, compite y prospera.",
    stat: null,
    hook: "Cada negocio que mejora hace más fuerte a toda su comunidad.",
    color: "#a84cc9",
    bg: "#0a030f",
  },
  {
    id: 17,
    act: "CIERRE",
    actLabel: "CIERRE",
    duration: 11,
    title: "Prueba la demo en vivo",
    visual:
      "Fondo negro elegante. Enlace de la demo grande y centrado: dentbotsonrisa.netlify.app. 'Tu agente listo en 15 minutos.'",
    narration:
      "Descubre cómo la inteligencia artificial transforma tu negocio y aporta al desarrollo de tu territorio. Prueba la demo ahora mismo.",
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
