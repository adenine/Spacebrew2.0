import { useState } from "react";
import type { RoutesMap } from "../types";
import { addRoute, deleteRoute, saveRoutes } from "../api";

// The patch-bay graph handles visualizing routes and creating new ones by
// dragging/clicking sockets; these manual fields cover typing in a route
// directly (e.g. for topics that aren't visible in the graph yet) and
// deleting, since Rete doesn't support click-to-delete on a connection path
// out of the box.
export function RoutesList({ routes, onChange }: { routes: RoutesMap; onChange: () => void }) {
  const [pubTopic, setPubTopic] = useState("");
  const [subTopic, setSubTopic] = useState("");

  async function onAdd() {
    if (!pubTopic || !subTopic) {
      alert("Please enter both topics");
      return;
    }
    await addRoute(pubTopic, subTopic);
    setPubTopic("");
    setSubTopic("");
    onChange();
  }

  async function onDelete(pub: string) {
    await deleteRoute(pub);
    onChange();
  }

  async function onSaveRoutes() {
    const res = await saveRoutes();
    alert(res.message);
  }

  const entries = Object.entries(routes);

  return (
    <div className="card routing-list">
      <h2>Active Routes</h2>
      <div className="publish__row">
        <input
          type="text"
          placeholder="Publisher Topic"
          value={pubTopic}
          onChange={(e) => setPubTopic(e.target.value)}
        />
        <input
          type="text"
          placeholder="Subscriber Topic"
          value={subTopic}
          onChange={(e) => setSubTopic(e.target.value)}
        />
        <button onClick={onAdd}>Add Route</button>
      </div>
      {entries.length === 0 ? (
        <p className="routing-list__empty">No routes yet — drag from a publisher's socket to a subscriber's to create one.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Publisher</th>
              <th>Subscriber</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {entries.map(([pub, sub]) => (
              <tr key={pub}>
                <td>{pub}</td>
                <td>{sub}</td>
                <td>
                  <button className="delete" onClick={() => onDelete(pub)}>
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      <div className="publish__row publish__row--actions routing-list__save-row">
        <button onClick={onSaveRoutes}>Save Routes to File</button>
      </div>
    </div>
  );
}
