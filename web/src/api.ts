import type { Client, RoutesMap, StatusResponse } from "./types";

async function json<T>(res: Response): Promise<T> {
  return (await res.json()) as T;
}

export function getStatus(): Promise<StatusResponse> {
  return fetch("/api/status").then((res) => json<StatusResponse>(res));
}

export function getClients(): Promise<Client[]> {
  return fetch("/api/clients").then((res) => json<Client[]>(res));
}

export function getRoutes(): Promise<RoutesMap> {
  return fetch("/api/routes").then((res) => json<RoutesMap>(res));
}

export function addRoute(pub: string, sub: string): Promise<{ message: string }> {
  return fetch("/api/routes", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ pub, sub }),
  }).then((res) => json<{ message: string }>(res));
}

export function deleteRoute(pub: string): Promise<{ message: string }> {
  return fetch(`/api/routes?pub=${encodeURIComponent(pub)}`, { method: "DELETE" }).then((res) =>
    json<{ message: string }>(res)
  );
}

export function publishMessage(topic: string, message: string): Promise<{ message: string }> {
  return fetch("/api/publish", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ topic, message }),
  }).then((res) => json<{ message: string }>(res));
}

export function saveRoutes(): Promise<{ message: string }> {
  return fetch("/api/save", { method: "POST" }).then((res) => json<{ message: string }>(res));
}

export function spawnTestClient(): Promise<{ message: string }> {
  return fetch("/api/testclient", { method: "POST" }).then((res) => json<{ message: string }>(res));
}
