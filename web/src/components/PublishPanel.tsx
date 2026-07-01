import { useState } from "react";
import { publishMessage } from "../api";

export function PublishPanel() {
  const [topic, setTopic] = useState("");
  const [message, setMessage] = useState("");

  async function onPublish() {
    if (!topic || !message) {
      alert("Please enter topic and message");
      return;
    }
    await publishMessage(topic, message);
    alert("Message published");
  }

  return (
    <div className="card publish">
      <h2>Publish Message</h2>
      <div className="publish__row">
        <input
          type="text"
          placeholder="Topic"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
        />
        <input
          type="text"
          placeholder="Message"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
        />
        <button onClick={onPublish}>Publish</button>
      </div>
    </div>
  );
}
