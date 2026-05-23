import { loadFont as loadInter } from "@remotion/google-fonts/Inter";
import { loadFont as loadPlayfair } from "@remotion/google-fonts/PlayfairDisplay";
import { loadFont as loadJetBrains } from "@remotion/google-fonts/JetBrainsMono";

let loaded = false;

export const loadFonts = () => {
  if (loaded) return;
  loaded = true;
  loadInter();
  loadPlayfair();
  loadJetBrains();
};

export const fontFamily = {
  body: "Inter, sans-serif",
  display: "'Playfair Display', Georgia, serif",
  mono: "'JetBrains Mono', monospace",
};
