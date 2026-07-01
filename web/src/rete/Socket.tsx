// Matches the original 2012 Spacebrew admin's connector dots: a small dark
// circle with a white ring, hanging half off the edge of its pub/sub bar
// (positioning is handled by .pubsub-node__socket in patchbay.css).
export function PubSubSocketComponent() {
  return <div className="pubsub-node__socket-dot" />;
}
