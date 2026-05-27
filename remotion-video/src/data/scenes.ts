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
    title: "El problema que nadie quiere vivir",
    visual:
      "Pantalla negra. Teléfono sonando a las 11:30 PM. Nadie contesta. Tres mensajes de WhatsApp sin respuesta con ticks grises.",
    narration:
      "Son las 11 de la noche. Tu cliente potencial está listo para comprar… pero nadie responde.",
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
      "Cada mensaje sin respuesta es una venta perdida. Una cita cancelada. Un cliente que no vuelve.",
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
    title: "Presentamos la solución",
    visual:
      "Transición a azul brillante. Logo del producto. WhatsApp y Telegram abiertos. Respuesta instantánea en 2 segundos.",
    narration:
      "Presentamos tu Agente Inteligente 24/7 — un asistente con IA que conoce tu negocio mejor que cualquier empleado.",
    stat: null,
    hook: "Responde en WhatsApp y Telegram. Sin apps. Sin instalaciones.",
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
      "Sube tus precios, servicios y políticas. El agente los aprende en minutos. Y responde exactamente como tú lo harías.",
    stat: "Configuración en menos de 15 minutos. Sin programar nada.",
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
      "Tu paciente tiene dolor a medianoche. Tu agente le responde de inmediato, le da opciones de cita y le tranquiliza.",
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
      "El agente recuerda la cita 24 horas antes y 2 horas antes. Si el paciente no puede, reagenda en ese mismo momento.",
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
    title: "Responde preguntas repetitivas",
    visual:
      "Asistente real agotada respondiendo lo mismo. Corte: el agente responde — precios, horarios, formas de pago.",
    narration:
      "¿Cuánto cuesta una limpieza? ¿Trabajan con seguro? Tu equipo deja de repetir lo mismo 30 veces al día.",
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
    title: "Resultado clínica dental",
    visual:
      "Dashboard: +40% citas, -65% cancelaciones, 0 llamadas perdidas. Dentista sonriendo.",
    narration:
      "Más citas. Menos cancelaciones. Menos trabajo repetitivo. Y pacientes que se sienten atendidos.",
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
      "Tu cliente está en el aeropuerto a las 2 de la mañana. Tu agente ya está ahí — respondiendo, guiando, tranquilizando.",
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
    title: "Ventas mientras duermes",
    visual:
      "Familia navegando paquetes a las 10 PM. Preguntan por Cancún. El agente cierra la venta.",
    narration:
      "Cuando tu competencia está dormida, tu agente está cerrando ventas, enviando cotizaciones y confirmando reservas.",
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
    title: "Soporte completo durante el viaje",
    visual:
      "Timeline: reserva → documentos → check-in → preguntas en destino → post-viaje. El agente presente en cada etapa.",
    narration:
      "Antes del viaje: documentos. Durante: soporte inmediato. Después: encuesta y próxima oferta. Todo automático.",
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
    title: "Resultado agencia de turismo",
    visual:
      "Dashboard: +55% conversión, 100% mensajes respondidos, 4.9★ satisfacción.",
    narration:
      "Más ventas. Mejor experiencia. Clientes que regresan. Y tú, disfrutando tu noche mientras el negocio trabaja solo.",
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
    title: "Por qué WhatsApp y Telegram",
    visual:
      "Comparativa: App nueva (nadie la descarga) vs WhatsApp (todos la tienen). 93% de penetración en Latinoamérica.",
    narration:
      "No le pides a tu cliente que descargue una app nueva. Le escribes por donde ya te escribe. Donde ya confía.",
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
    title: "Solo sabe lo que tú le enseñas",
    visual:
      "El agente responde SOLO con información de la empresa. 'No tengo esa información, te pongo en contacto con un asesor.'",
    narration:
      "El agente no improvisa. Solo responde con la información que tú le das. Si no lo sabe, lo dice.",
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
    title: "Crece con tu negocio",
    visual:
      "Un bot → 10 conversaciones. Mismo bot → 500 conversaciones simultáneas. Sin contratar más gente.",
    narration:
      "¿Tienes 10 clientes o 500? El agente responde a todos al mismo tiempo, con la misma calidad, sin demoras.",
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
    title: "Para cualquier tipo de negocio",
    visual:
      "Carrusel: clínica dental · agencia de turismo · restaurante · inmobiliaria · academia · spa · tienda · consultorio.",
    narration:
      "¿Tienes clientes que te hacen preguntas repetitivas? ¿Pierdes ventas fuera de horario? Esto es para ti.",
    stat: null,
    hook: "Si tienes clientes, tienes un caso de uso.",
    color: "#a84cc9",
    bg: "#0a030f",
  },
  {
    id: 17,
    act: "CIERRE",
    actLabel: "CIERRE",
    duration: 11,
    title: "Agenda tu demo gratis",
    visual:
      "Fondo negro elegante. Número de WhatsApp. QR code. 'Agenda tu demo gratis'. 'Tu agente listo en 15 minutos'.",
    narration:
      "¿Quieres ver cómo funciona con tu negocio? Agenda una demo gratuita. En 15 minutos configuras tu agente.",
    stat: null,
    hook: "Demo gratuita · Sin contratos · Operativo hoy mismo",
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
