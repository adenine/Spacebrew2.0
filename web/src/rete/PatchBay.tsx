import { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import { NodeEditor, ClassicPreset } from "rete";
import { AreaPlugin, AreaExtensions } from "rete-area-plugin";
import { ConnectionPlugin, ClassicFlow } from "rete-connection-plugin";
import { ReactPlugin, Presets } from "rete-react-plugin";
import type { ReactArea2D } from "rete-react-plugin";
import { createPubSubNode } from "./model";
import type { NodeMeta, Schemes } from "./model";
import { PubSubNodeComponent } from "./PubSubNode";
import { PubSubSocketComponent } from "./Socket";
import { PatchConnection } from "./PatchConnection";
import type { Client, RoutesMap } from "../types";
import "./patchbay.css";

// Node is 29px tall (patchbay.css); the 15px gap between same-client rows
// is a third of that (5px), giving a 34px row pitch.
export const ROW_HEIGHT = 34;
export const NODE_WIDTH = 260;
export const COLUMN_GAP = 140;
export const CLIENT_GAP = 20;
const PUB_X = 0;
const MIN_GRAPH_WIDTH = PUB_X + NODE_WIDTH + COLUMN_GAP + NODE_WIDTH;

function normalizeType(type: string): string {
  const t = type.toLowerCase().trim();
  return t === "bool" ? "boolean" : t;
}

type AreaExtra = ReactArea2D<Schemes>;

interface LayoutEntry extends NodeMeta {
  x: number;
  y: number;
}

export interface ClientLayout {
  client: Client;
  y: number;
  height: number;
}

function buildLayout(clients: Client[], graphWidth: number) {
  const entries: LayoutEntry[] = [];
  const clientLayouts: ClientLayout[] = [];
  const subX = Math.max(graphWidth - NODE_WIDTH, PUB_X + NODE_WIDTH + COLUMN_GAP);
  let y = 0;

  for (const client of clients) {
    const rowCount = Math.max(client.publishers.length, client.subscribers.length, 1);
    const blockHeight = rowCount * ROW_HEIGHT;

    client.publishers.forEach((entry, i) => {
      const [entryName, entryType = ""] = entry.split(":");
      entries.push({
        topic: `${client.name}/${entryName.trim()}`,
        entryName: entryName.trim(),
        entryType: entryType.trim(),
        kind: "pub",
        clientName: client.name,
        x: PUB_X,
        y: y + i * ROW_HEIGHT,
      });
    });

    client.subscribers.forEach((entry, i) => {
      const [entryName, entryType = ""] = entry.split(":");
      entries.push({
        topic: `${client.name}/${entryName.trim()}`,
        entryName: entryName.trim(),
        entryType: entryType.trim(),
        kind: "sub",
        clientName: client.name,
        x: subX,
        y: y + i * ROW_HEIGHT,
      });
    });

    clientLayouts.push({ client, y, height: blockHeight });
    y += blockHeight + CLIENT_GAP;
  }

  return { entries, clientLayouts, totalHeight: Math.max(y - CLIENT_GAP, 0), subX };
}

function nodeId(kind: "pub" | "sub", topic: string): string {
  return `${kind}:${topic}`;
}

interface EditorHandle {
  editor: NodeEditor<Schemes>;
  area: AreaPlugin<Schemes, AreaExtra>;
  positions: Map<string, { x: number; y: number }>;
  metaMap: Map<string, NodeMeta>;
}

export interface PatchBayProps {
  clients: Client[];
  routes: RoutesMap;
  onCreateRoute: (pub: string, sub: string) => void;
  onLayout?: (clientLayouts: ClientLayout[], totalHeight: number) => void;
}

export function PatchBay({ clients, routes, onCreateRoute, onLayout }: PatchBayProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const handleRef = useRef<EditorHandle | null>(null);
  const onCreateRouteRef = useRef(onCreateRoute);
  onCreateRouteRef.current = onCreateRoute;
  const [graphWidth, setGraphWidth] = useState(MIN_GRAPH_WIDTH);
  const [canvasHeight, setCanvasHeight] = useState(0);
  const [dividerX, setDividerX] = useState(0);

  // Track the graph's rendered width so the subscriber column can stay
  // right-aligned against it.
  useEffect(() => {
    if (!containerRef.current) return;
    const el = containerRef.current;
    const observer = new ResizeObserver((entries) => {
      const width = entries[0]?.contentRect.width;
      if (width) setGraphWidth(Math.max(width, MIN_GRAPH_WIDTH));
    });
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  // One-time editor setup.
  useEffect(() => {
    if (!containerRef.current) return;

    const editor = new NodeEditor<Schemes>();
    const area = new AreaPlugin<Schemes, AreaExtra>(containerRef.current);
    const connection = new ConnectionPlugin<Schemes, AreaExtra>();
    const render = new ReactPlugin<Schemes, AreaExtra>({ createRoot });
    const positions = new Map<string, { x: number; y: number }>();
    const metaMap = new Map<string, NodeMeta>();

    render.addPreset(
      Presets.classic.setup({
        customize: {
          node() {
            return (nodeProps) => {
              const meta = metaMap.get(nodeProps.data.id);
              if (!meta) return null;
              const connected = editor
                .getConnections()
                .some((c) => c.source === nodeProps.data.id || c.target === nodeProps.data.id);
              return <PubSubNodeComponent {...nodeProps} meta={meta} connected={connected} />;
            };
          },
          socket() {
            return PubSubSocketComponent;
          },
          connection() {
            return PatchConnection;
          },
        },
      })
    );
    // Publishers can only route to subscribers declaring the same type
    // (boolean -> boolean, range -> range, etc).
    connection.addPreset(
      () =>
        new ClassicFlow<Schemes, unknown[]>({
          canMakeConnection: (from, to) => {
            // A click (down+up on the same socket) routes both events
            // through this check via Rete's pick/drop state machine. Without
            // this guard, the "up" half of the first click would compare a
            // socket to itself, match trivially on type, and reset the
            // picked state before the second socket is ever clicked.
            if (from.nodeId === to.nodeId) return false;
            const fromMeta = metaMap.get(from.nodeId);
            const toMeta = metaMap.get(to.nodeId);
            if (!fromMeta || !toMeta) return false;
            return normalizeType(fromMeta.entryType) === normalizeType(toMeta.entryType);
          },
        })
    );

    editor.use(area);
    area.use(connection);
    area.use(render);

    // Freeze pan/zoom: this is a fixed two-column diagram, not a freely
    // navigable canvas.
    AreaExtensions.restrictor(area, {
      scaling: () => ({ min: 1, max: 1 }),
      translation: () => ({ left: 0, top: 0, right: 0, bottom: 0 }),
    });

    // Nodes live at positions computed from client data (see buildLayout).
    // If a node gets dragged, snap it back once the drag ends.
    area.addPipe((context) => {
      if (context.type === "nodetranslated") {
        const assigned = positions.get(context.data.id);
        if (assigned) {
          const current = area.nodeViews.get(context.data.id)?.position;
          if (current && (current.x !== assigned.x || current.y !== assigned.y)) {
            area.translate(context.data.id, assigned);
          }
        }
      }
      return context;
    });

    editor.addPipe((context) => {
      if (context.type === "connectioncreated") {
        const conn = context.data;
        const source = metaMap.get(conn.source);
        const target = metaMap.get(conn.target);
        if (source && target) {
          onCreateRouteRef.current(source.topic, target.topic);
        }
      }
      // Re-render both endpoint nodes so their socket dots reflect the new
      // connected/unconnected state.
      if (context.type === "connectioncreated" || context.type === "connectionremoved") {
        const conn = context.data;
        void area.update("node", conn.source);
        void area.update("node", conn.target);
      }
      return context;
    });

    handleRef.current = { editor, area, positions, metaMap };

    return () => {
      area.destroy();
      handleRef.current = null;
    };
  }, []);

  // Sync nodes/connections whenever clients or routes change.
  useEffect(() => {
    const handle = handleRef.current;
    if (!handle) return;
    const { editor, area, positions, metaMap } = handle;

    (async () => {
      const { entries, clientLayouts, totalHeight, subX } = buildLayout(clients, graphWidth);
      onLayout?.(clientLayouts, totalHeight);
      // Rete positions nodes via CSS transform, which doesn't contribute to
      // an auto-height parent's size, so the container needs an explicit
      // height or the (very much present) nodes render outside its 0-height
      // box.
      if (containerRef.current) {
        containerRef.current.style.height = `${totalHeight}px`;
      }
      setCanvasHeight(totalHeight);
      setDividerX((NODE_WIDTH + subX) / 2);

      const desiredIds = new Set(entries.map((e) => nodeId(e.kind, e.topic)));

      for (const node of editor.getNodes()) {
        if (!desiredIds.has(node.id)) {
          for (const conn of editor.getConnections()) {
            if (conn.source === node.id || conn.target === node.id) {
              await editor.removeConnection(conn.id);
            }
          }
          await editor.removeNode(node.id);
          positions.delete(node.id);
          metaMap.delete(node.id);
        }
      }

      for (const entry of entries) {
        const id = nodeId(entry.kind, entry.topic);
        let node = editor.getNode(id);
        if (!node) {
          node = createPubSubNode(entry);
          node.id = id;
          metaMap.set(id, entry);
          await editor.addNode(node);
        } else {
          metaMap.set(id, entry);
        }
        positions.set(id, { x: entry.x, y: entry.y });
        await area.translate(id, { x: entry.x, y: entry.y });
      }

      const desiredConnKeys = new Set(Object.entries(routes).map(([pub, sub]) => `${pub}=>${sub}`));
      for (const conn of editor.getConnections()) {
        const source = metaMap.get(conn.source);
        const target = metaMap.get(conn.target);
        if (!source || !target || !desiredConnKeys.has(`${source.topic}=>${target.topic}`)) {
          await editor.removeConnection(conn.id);
        }
      }
      for (const [pub, sub] of Object.entries(routes)) {
        const pubId = nodeId("pub", pub);
        const subId = nodeId("sub", sub);
        const pubNode = editor.getNode(pubId);
        const subNode = editor.getNode(subId);
        if (!pubNode || !subNode) continue;
        const already = editor
          .getConnections()
          .some((c) => c.source === pubId && c.target === subId);
        if (!already) {
          await editor.addConnection(new ClassicPreset.Connection(pubNode, "out", subNode, "in"));
        }
      }
    })();
  }, [clients, routes, onLayout, graphWidth]);

  return (
    <div className="patchbay-canvas-wrap">
      <div
        className="patchbay-divider"
        style={{ left: dividerX, height: canvasHeight }}
      />
      <div ref={containerRef} className="patchbay-canvas" />
    </div>
  );
}
