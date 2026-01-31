import { useEffect, useMemo, useState } from "react";
import "./App.css";

type FrequencyRow = {
  sample: string;
  total_count: number;
  population: string;
  count: number;
  percentage: number;
};

const API_BASE = "";

function fmtInt(n: number) {
  return new Intl.NumberFormat().format(n);
}

function fmtPct(n: number) {
  return `${n.toFixed(2)}%`;
}

export default function App() {
  const [limit, setLimit] = useState<number>(200);
  const [rows, setRows] = useState<FrequencyRow[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const apiHealthUrl = `${API_BASE}/api/v1/health`;
  const apiFreqUrl = `${API_BASE}/api/v1/frequency?limit=${limit}`;

  // Derive list of samples for quick filtering on the client (optional)
  const samples = useMemo(() => {
    const set = new Set(rows.map((r) => r.sample));
    return Array.from(set).sort();
  }, [rows]);

  const [sampleFilter, setSampleFilter] = useState<string>("");

  const filteredRows = useMemo(() => {
    if (!sampleFilter) return rows;
    return rows.filter((r) => r.sample === sampleFilter);
  }, [rows, sampleFilter]);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(apiFreqUrl);
        if (!res.ok) {
          throw new Error(`API error: ${res.status} ${res.statusText}`);
        }
        const data = (await res.json()) as FrequencyRow[];
        if (!cancelled) setRows(data);
      } catch (e: any) {
        if (!cancelled) setError(e?.message ?? "Unknown error");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [apiFreqUrl]);

  return (
    <div style={{ maxWidth: 1100, margin: "0 auto", padding: 24 }}>
      <h1>Cell Counts Dashboard</h1>

      <div style={{ marginBottom: 12 }}>
        <div>
          API base: <code>{API_BASE}</code>
        </div>
        <div>
          Health:{" "}
          <a href={apiHealthUrl} target="_blank" rel="noreferrer">
            {apiHealthUrl}
          </a>
        </div>
        <div>
          Frequency endpoint:{" "}
          <a href={apiFreqUrl} target="_blank" rel="noreferrer">
            {apiFreqUrl}
          </a>
        </div>
      </div>

      <div
        style={{
          display: "flex",
          gap: 12,
          alignItems: "center",
          flexWrap: "wrap",
          marginBottom: 12,
        }}
      >
        <label>
          Limit:{" "}
          <select
            value={limit}
            onChange={(e) => setLimit(Number(e.target.value))}
          >
            <option value={50}>50</option>
            <option value={200}>200</option>
            <option value={500}>500</option>
            <option value={2000}>2000</option>
            <option value={10000}>10000</option>
          </select>
        </label>

        <label>
          Sample:{" "}
          <select
            value={sampleFilter}
            onChange={(e) => setSampleFilter(e.target.value)}
            disabled={samples.length === 0}
          >
            <option value="">All samples</option>
            {samples.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </label>

        {loading ? <span>Loading…</span> : null}
        {error ? <span style={{ color: "crimson" }}>Error: {error}</span> : null}
      </div>

      <div style={{ border: "1px solid #ddd", borderRadius: 8, overflow: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ background: "#fafafa", color: "#111" }}>
              <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #eee", fontWeight: 700 }}>sample</th>
              <th style={{ textAlign: "right", padding: 10, borderBottom: "1px solid #eee", fontWeight: 700 }}>total_count</th>
              <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #eee", fontWeight: 700 }}>population</th>
              <th style={{ textAlign: "right", padding: 10, borderBottom: "1px solid #eee", fontWeight: 700 }}>count</th>
              <th style={{ textAlign: "right", padding: 10, borderBottom: "1px solid #eee", fontWeight: 700 }}>percentage</th>
            </tr>
          </thead>
          <tbody>
            {filteredRows.map((r, idx) => (
              <tr key={`${r.sample}-${r.population}-${idx}`}>
                <td style={{ padding: 10, borderBottom: "1px solid #f2f2f2" }}>{r.sample}</td>
                <td style={{ padding: 10, textAlign: "right", borderBottom: "1px solid #f2f2f2" }}>
                  {fmtInt(r.total_count)}
                </td>
                <td style={{ padding: 10, borderBottom: "1px solid #f2f2f2" }}>{r.population}</td>
                <td style={{ padding: 10, textAlign: "right", borderBottom: "1px solid #f2f2f2" }}>
                  {fmtInt(r.count)}
                </td>
                <td style={{ padding: 10, textAlign: "right", borderBottom: "1px solid #f2f2f2" }}>
                  {fmtPct(r.percentage)}
                </td>
              </tr>
            ))}

            {!loading && !error && filteredRows.length === 0 ? (
              <tr>
                <td colSpan={5} style={{ padding: 12 }}>
                  No rows returned.
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
    </div>
  );
}