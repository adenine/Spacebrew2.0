import { Presets } from "rete-react-plugin";

const { useConnection } = Presets.classic;

export function PatchConnection() {
  const { path } = useConnection();
  if (!path) return null;
  return (
    <svg
      style={{
        overflow: "visible",
        position: "absolute",
        pointerEvents: "none",
        width: 9999,
        height: 9999,
      }}
    >
      <path d={path} fill="none" stroke="#1c1c1c" strokeWidth={2} style={{ pointerEvents: "auto" }} />
    </svg>
  );
}
