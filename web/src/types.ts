export interface Client {
  name: string;
  description: string;
  publishers: string[]; // "name:type" entries
  subscribers: string[]; // "name:type" entries
}

// Publisher topic -> subscriber topic
export type RoutesMap = Record<string, string>;

export interface StatusResponse {
  connected: boolean;
  broker: string;
  port: number;
}

export interface RouteActivityEvent {
  pub: string;
  sub: string;
  message: string;
}

export interface TopicMessageEvent {
  topic: string;
  message: string;
}

export type WsEvent = Partial<RouteActivityEvent> & Partial<TopicMessageEvent>;
