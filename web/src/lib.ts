import type { Client } from "./types";

export interface TopicMessage {
  message: string;
  ts: number;
}

// A client's pub/sub entries are "name:type" strings; the actual MQTT topic
// they communicate on is "clientName/name".
export function clientTopics(client: Client): string[] {
  const names = [...client.publishers, ...client.subscribers].map((entry) => entry.split(":")[0].trim());
  return names.map((name) => `${client.name}/${name}`);
}

export function latestMessageForTopics(
  topics: string[],
  topicMessages: Record<string, TopicMessage>
): string {
  let latest: TopicMessage | null = null;
  for (const topic of topics) {
    const entry = topicMessages[topic];
    if (entry && (!latest || entry.ts > latest.ts)) {
      latest = entry;
    }
  }
  return latest ? latest.message : "—";
}
