import type { Orientation } from "../../Video";

export const visualBox = (orientation: Orientation): React.CSSProperties => ({
  position: "absolute",
  top: orientation === "portrait" ? "32%" : "30%",
  left: 0,
  right: 0,
  bottom: orientation === "portrait" ? "42%" : "32%",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  padding: orientation === "portrait" ? "0 60px" : "0 90px",
});
