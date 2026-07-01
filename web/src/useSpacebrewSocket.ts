import { useEffect, useRef } from "react";
import type { WsEvent } from "./types";

export function useSpacebrewSocket(onEvent: (event: WsEvent) => void) {
  const handlerRef = useRef(onEvent);
  handlerRef.current = onEvent;

  useEffect(() => {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws`);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data) as WsEvent;
      handlerRef.current(data);
    };

    return () => ws.close();
  }, []);
}
