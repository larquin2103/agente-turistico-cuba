import type { Scene } from "../../data/scenes";
import type { Orientation } from "../../Video";
import { ProblemPhone } from "./ProblemPhone";
import { LostMoney } from "./LostMoney";
import { LogoReveal } from "./LogoReveal";
import { HowItWorks } from "./HowItWorks";
import { WhatsAppChat } from "./WhatsAppChat";
import { BeforeAfter } from "./BeforeAfter";
import { TiredVsBot } from "./TiredVsBot";
import { Dashboard } from "./Dashboard";
import { TravelTimeline } from "./TravelTimeline";
import { PlatformCompare } from "./PlatformCompare";
import { GroundedBot } from "./GroundedBot";
import { ScaleViz } from "./ScaleViz";
import { BusinessCarousel } from "./BusinessCarousel";
import { CallToAction } from "./CallToAction";

export const SceneVisual: React.FC<{
  scene: Scene;
  orientation: Orientation;
}> = ({ scene, orientation }) => {
  // Routing por escena
  switch (scene.id) {
    case 1:
      return <ProblemPhone orientation={orientation} />;
    case 2:
      return <LostMoney orientation={orientation} />;
    case 3:
      return <LogoReveal orientation={orientation} color={scene.color} />;
    case 4:
      return <HowItWorks orientation={orientation} color={scene.color} />;
    case 5:
      return (
        <WhatsAppChat
          orientation={orientation}
          color={scene.color}
          context="dental_midnight"
        />
      );
    case 6:
      return <BeforeAfter orientation={orientation} color={scene.color} />;
    case 7:
      return <TiredVsBot orientation={orientation} color={scene.color} />;
    case 8:
      return (
        <Dashboard
          orientation={orientation}
          color={scene.color}
          metrics={[
            { label: "Citas agendadas", value: "+40%", trend: "up" },
            { label: "Cancelaciones", value: "-65%", trend: "down-good" },
            { label: "Llamadas perdidas", value: "0", trend: "up" },
          ]}
        />
      );
    case 9:
      return (
        <WhatsAppChat
          orientation={orientation}
          color={scene.color}
          context="travel_airport"
        />
      );
    case 10:
      return (
        <WhatsAppChat
          orientation={orientation}
          color={scene.color}
          context="travel_sale"
        />
      );
    case 11:
      return <TravelTimeline orientation={orientation} color={scene.color} />;
    case 12:
      return (
        <Dashboard
          orientation={orientation}
          color={scene.color}
          metrics={[
            { label: "Conversión", value: "+55%", trend: "up" },
            { label: "Mensajes resp.", value: "100%", trend: "up" },
            { label: "Satisfacción", value: "4.9★", trend: "up" },
          ]}
        />
      );
    case 13:
      return <PlatformCompare orientation={orientation} color={scene.color} />;
    case 14:
      return <GroundedBot orientation={orientation} color={scene.color} />;
    case 15:
      return <ScaleViz orientation={orientation} color={scene.color} />;
    case 16:
      return <BusinessCarousel orientation={orientation} color={scene.color} />;
    case 17:
      return <CallToAction orientation={orientation} color={scene.color} />;
    default:
      return null;
  }
};
