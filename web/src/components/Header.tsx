import type { StatusResponse } from "../types";

export function Header({
  status,
  clientCount,
}: {
  status: StatusResponse | null;
  clientCount: number;
}) {
  return (
    <header className="app-header">
      <h1>Spacebrew 2.0</h1>
      <div className="app-header__status">
        <span>
          <strong>Clients Connected:</strong> {clientCount}
        </span>
        {status && (
          <span>
            <strong>Server:</strong> {status.broker}:{status.port}
          </span>
        )}
        <span>
          <strong>Status:</strong>{" "}
          <span className={status?.connected ? "status-connected" : "status-disconnected"}>
            {status?.connected ? "Connected" : "Disconnected"}
          </span>
        </span>
      </div>
    </header>
  );
}
