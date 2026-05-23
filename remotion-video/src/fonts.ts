import { loadFont as loadInter } from "@remotion/google-fonts/Inter";
import { loadFont as loadPlayfair } from "@remotion/google-fonts/PlayfairDisplay";
import { loadFont as loadJetBrains } from "@remotion/google-fonts/JetBrainsMono";

let loaded = false;

export const loadFonts = () => {
  if (loaded) return;
  loaded = true;
  loadInter("normal", {
    weights: ["400", "500", "600", "700"],
    subsets: ["latin"],
    ignoreTooManyRequestsWarning: true,
  });
  loadPlayfair("normal", {
    weights: ["400", "500", "600", "700"],
    subsets: ["latin"],
    ignoreTooManyRequestsWarning: true,
  });
  loadJetBrains("normal", {
    weights: ["400", "500", "600", "700"],
    subsets: ["latin"],
    ignoreTooManyRequestsWarning: true,
  });
};

export const fontFamily = {
  body: "Inter, sans-serif",
  display: "'Playfair Display', Georgia, serif",
  mono: "'JetBrains Mono', monospace",
};
