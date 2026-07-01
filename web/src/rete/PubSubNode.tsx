import type { PointerEvent } from "react";
import { Presets } from "rete-react-plugin";
import type { RenderEmit } from "rete-react-plugin";
import type { ClassicPreset } from "rete";
import type { NodeMeta } from "./model";
import type { Schemes } from "./model";

const { RefSocket } = Presets.classic;

const TYPE_COLORS: Record<string, string> = {
  boolean: "#ffae00",
  bool: "#ffae00",
  range: "#c600f8",
  string: "#ff0000",
  json: "#111111",
  number: "#111111",
};

function typeColor(type: string): string {
  return TYPE_COLORS[type.toLowerCase().trim()] ?? "#888888";
}

export function PubSubNodeComponent(props: {
  data: ClassicPreset.Node;
  emit: RenderEmit<Schemes>;
  meta: NodeMeta;
  connected: boolean;
}) {
  const { data, emit, meta, connected } = props;
  const isPub = meta.kind === "pub";
  const color = typeColor(meta.entryType);

  const socket = isPub ? (
    <RefSocket
      name="output-socket"
      side="output"
      socketKey="out"
      nodeId={data.id}
      emit={emit}
      payload={data.outputs.out!.socket}
    />
  ) : (
    <RefSocket
      name="input-socket"
      side="input"
      socketKey="in"
      nodeId={data.id}
      emit={emit}
      payload={data.inputs.in!.socket}
    />
  );

  const badge = (
    <span className="pubsub-node__badge" style={{ background: color }}>
      {meta.entryType || "?"}
    </span>
  );
  const label = <span className="pubsub-node__label">{meta.entryName}</span>;
  const socketWrap = (
    <span className={`pubsub-node__socket ${connected ? "pubsub-node__socket--connected" : ""}`}>
      {socket}
    </span>
  );

  // Nodes sit at fixed positions (see PatchBay's layout); block Rete's
  // built-in node-drag from starting unless the pointerdown is on the
  // socket itself, which needs to bubble up to the connection plugin.
  const blockNodeDrag = (event: PointerEvent) => {
    if (!(event.target as HTMLElement).closest(".pubsub-node__socket")) {
      event.stopPropagation();
    }
  };

  return (
    <div
      className={`pubsub-node ${isPub ? "pubsub-node--pub" : "pubsub-node--sub"} ${
        connected ? "pubsub-node--connected" : ""
      }`}
      onPointerDown={blockNodeDrag}
    >
      {isPub ? (
        <>
          {badge}
          {label}
          {socketWrap}
        </>
      ) : (
        <>
          {socketWrap}
          {label}
          {badge}
        </>
      )}
    </div>
  );
}
