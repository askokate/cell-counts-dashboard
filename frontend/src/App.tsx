import { useEffect, useState } from "react";

export default function App() {
  const [status, setStatus] = useState("loading...");
  const API = import.meta.env.VITE_API_BASE_URL;

  useEffect(() => {
    fetch(`${API}/api/v1/health`)
      .then((r) => r.json())
      .then((d) => setStatus(d.status))
      .catch(() => setStatus("error"));
  }, [API]);

  return (
    <div style={{ padding: 24, fontFamily: "system-ui" }}>
      <h1>Cell Counts Dashboard</h1>
      <p><b>API status:</b> {status}</p>
      <p><b>API base:</b> {API}</p>
    </div>
  );
}