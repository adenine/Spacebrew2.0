import { spawnTestClient } from "../api";

export function TestingTools() {
  async function onSpawnTestClient() {
    const res = await spawnTestClient();
    alert(res.message);
  }

  return (
    <div className="card testing-tools">
      <h2>Testing Tools</h2>
      <div className="publish__row publish__row--actions">
        <button onClick={onSpawnTestClient}>Spawn Test Client</button>
        <a href="/webclient" target="_blank" rel="noreferrer" className="button-link">
          Open Web Client ↗
        </a>
      </div>
    </div>
  );
}
