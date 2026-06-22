import type { Orientation } from "../../Video";

// El visual llena el contenedor que le asigna SceneRenderer (columna derecha
// en horizontal, banda central en vertical). Así nunca se superpone al texto.
export const visualBox = (_orientation?: Orientation): React.CSSProperties => ({
  position: "absolute",
  inset: 0,
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  padding: 12,
  overflow: "hidden",
});
