import type { ClientLayout } from "../rete/PatchBay";
import type { TopicMessage } from "../lib";
import { clientTopics, latestMessageForTopics } from "../lib";

export function ClientsSidebar({
  clientLayouts,
  totalHeight,
  topicMessages,
  activeTopics,
}: {
  clientLayouts: ClientLayout[];
  totalHeight: number;
  topicMessages: Record<string, TopicMessage>;
  activeTopics: Set<string>;
}) {
  return (
    <div className="clients-sidebar" style={{ height: totalHeight }}>
      {clientLayouts.map(({ client, y, height }) => {
        const topics = clientTopics(client);
        const message = latestMessageForTopics(topics, topicMessages);
        const isActive = topics.some((t) => activeTopics.has(t));
        return (
          <div key={client.name} className="client-row" style={{ top: y, height }}>
            <span className={`client-row__led ${isActive ? "client-row__led--active" : ""}`} />
            <div className="client-row__body">
              <div className="client-row__name">{client.name}</div>
              <div className="client-row__desc">{client.description}</div>
              <div className="client-row__message">{message}</div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
