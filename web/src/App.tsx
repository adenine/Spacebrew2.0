import { useCallback, useEffect, useRef, useState } from "react";
import "./App.css";
import { Header } from "./components/Header";
import { Footer } from "./components/Footer";
import { PublishPanel } from "./components/PublishPanel";
import { RoutesList } from "./components/RoutesList";
import { TestingTools } from "./components/TestingTools";
import { ClientsSidebar } from "./components/ClientsSidebar";
import { PatchBay } from "./rete/PatchBay";
import type { ClientLayout } from "./rete/PatchBay";
import { addRoute, getClients, getRoutes, getStatus } from "./api";
import { useSpacebrewSocket } from "./useSpacebrewSocket";
import type { Client, RoutesMap, StatusResponse } from "./types";
import type { TopicMessage } from "./lib";

const POLL_INTERVAL_MS = 5000;
const BLINK_MS = 200;

function App() {
  const [status, setStatus] = useState<StatusResponse | null>(null);
  const [clients, setClients] = useState<Client[]>([]);
  const [routes, setRoutes] = useState<RoutesMap>({});
  const [topicMessages, setTopicMessages] = useState<Record<string, TopicMessage>>({});
  const [activeTopics, setActiveTopics] = useState<Set<string>>(new Set());
  const [clientLayouts, setClientLayouts] = useState<ClientLayout[]>([]);
  const [totalHeight, setTotalHeight] = useState(0);

  const refreshClients = useCallback(() => {
    getClients().then(setClients).catch(console.error);
  }, []);
  const refreshRoutes = useCallback(() => {
    getRoutes().then(setRoutes).catch(console.error);
  }, []);
  const refreshStatus = useCallback(() => {
    getStatus().then(setStatus).catch(console.error);
  }, []);

  useEffect(() => {
    refreshStatus();
    refreshClients();
    refreshRoutes();
    const id = setInterval(() => {
      refreshStatus();
      refreshClients();
      refreshRoutes();
    }, POLL_INTERVAL_MS);
    return () => clearInterval(id);
  }, [refreshStatus, refreshClients, refreshRoutes]);

  const blinkTimers = useRef<Record<string, ReturnType<typeof setTimeout>>>({});
  const blink = useCallback((topic: string) => {
    setActiveTopics((prev) => new Set(prev).add(topic));
    clearTimeout(blinkTimers.current[topic]);
    blinkTimers.current[topic] = setTimeout(() => {
      setActiveTopics((prev) => {
        const next = new Set(prev);
        next.delete(topic);
        return next;
      });
    }, BLINK_MS);
  }, []);

  useSpacebrewSocket((event) => {
    if (event.pub) blink(event.pub);
    if (event.sub) blink(event.sub);
    if (event.topic) {
      blink(event.topic);
      setTopicMessages((prev) => ({
        ...prev,
        [event.topic!]: { message: event.message ?? "", ts: Date.now() },
      }));
    }
  });

  const onCreateRoute = useCallback(
    (pub: string, sub: string) => {
      addRoute(pub, sub)
        .catch(console.error)
        .finally(refreshRoutes);
    },
    [refreshRoutes]
  );

  const onLayout = useCallback((layouts: ClientLayout[], height: number) => {
    setClientLayouts(layouts);
    setTotalHeight(height);
  }, []);

  return (
    <div className="app">
      <Header status={status} clientCount={clients.length} />

      <div className="card">
        <h2>Patch Bay</h2>
        <div className="patchbay">
          <div className="patchbay__sidebar-wrap">
            <div className="patchbay__column-label">Clients</div>
            <ClientsSidebar
              clientLayouts={clientLayouts}
              totalHeight={totalHeight}
              topicMessages={topicMessages}
              activeTopics={activeTopics}
            />
          </div>
          <div className="patchbay__graph">
            <div className="patchbay__columns">
              <div className="patchbay__column-label">Publishers</div>
              <div className="patchbay__column-label patchbay__column-label--sub">Subscribers</div>
            </div>
            <PatchBay clients={clients} routes={routes} onCreateRoute={onCreateRoute} onLayout={onLayout} />
          </div>
        </div>
      </div>

      <RoutesList routes={routes} onChange={refreshRoutes} />
      <PublishPanel />
      <TestingTools />
      <Footer />
    </div>
  );
}

export default App;
