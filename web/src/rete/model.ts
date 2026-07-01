import { ClassicPreset } from "rete";
import type { ClassicScheme } from "rete-react-plugin";

export const pubSubSocket = new ClassicPreset.Socket("pubsub");

export type EntryKind = "pub" | "sub";

export interface NodeMeta {
  topic: string;
  entryName: string;
  entryType: string;
  kind: EntryKind;
  clientName: string;
}

// Rete's generic constraints get unhappy about custom Node subclasses with
// extra fields, so node metadata (topic, type, etc) is tracked in a side Map
// (see PatchBay's `metaMap`) instead of subclassing ClassicPreset.Node.
export function createPubSubNode(meta: NodeMeta): ClassicPreset.Node {
  const node = new ClassicPreset.Node(meta.entryName);
  if (meta.kind === "pub") {
    // A publisher topic maps to exactly one subscriber per
    // router.py's `routes[pub] = sub` model, so only one outgoing
    // connection is allowed.
    node.addOutput("out", new ClassicPreset.Output(pubSubSocket, "", false));
  } else {
    // Multiple publishers can route to the same subscriber topic.
    node.addInput("in", new ClassicPreset.Input(pubSubSocket, "", true));
  }
  return node;
}

export type Schemes = ClassicScheme;
