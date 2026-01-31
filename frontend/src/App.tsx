import { useEffect, useMemo, useState } from "react";
import "./App.css";

// ---- Chart.js boxplot imports ----
import {
  Chart as ChartJS,
  LinearScale,
  CategoryScale,
  Tooltip,
  Legend,
  Title,
  type ChartOptions,
  type ChartData,
} from "chart.js";
import { BoxPlotController, BoxAndWiskers } from "@sgratzl/chartjs-chart-boxplot";
import { Chart } from "react-chartjs-2";

// Register once
ChartJS.register(
  LinearScale,
  CategoryScale,
  Tooltip,
  Legend,
  Title,
  BoxPlotController,
  BoxAndWiskers
);

// --- Global Chart defaults for dark UI ---
ChartJS.defaults.color = "#E5E7EB"; // light gray text
ChartJS.defaults.borderColor = "rgba(255,255,255,0.15)"; // subtle grid/borders
ChartJS.defaults.font.family =
  'ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji", "Segoe UI Emoji"';

// ---------------- Types ----------------
type FrequencyRow = {
  sample: string;
  total_count: number;
  population: string;
  count: number;
  percentage: number;
};

type Part3Row = {
  sample: string;
  response: "yes" | "no";
  population: string;
  percentage: number;
};

type Part3StatRow = {
  population: string;
  n_yes: number;
  n_no: number;
  median_yes: number;
  median_no: number;
  u_statistic: number;
  p_value: number;
  significant_p_lt_0_05: boolean;
  q_value?: number;
  significant_fdr_0_05?: boolean;
};

const API_BASE =
  import.meta.env.VITE_API_BASE_URL?.toString()?.trim() || "";

// ---------------- Format helpers ----------------
function fmtInt(n: number) {
  return new Intl.NumberFormat().format(n);
}

function fmtPct(n: number) {
  return `${n.toFixed(2)}%`;
}

function fmtP(n: number) {
  if (!Number.isFinite(n)) return "NA";
  if (n < 0.001) return "<0.001";
  return n.toFixed(3);
}

// -------------- UI helpers --------------
function pillStyle(active: boolean): React.CSSProperties {
  return {
    padding: "8px 12px",
    borderRadius: 999,
    border: "1px solid #ddd",
    background: active ? "#111" : "#fff",
    color: active ? "#fff" : "#111",
    cursor: "pointer",
    fontWeight: 600,
  };
}

export default function App() {
  // ---------------- Tabs ----------------
  const [activeTab, setActiveTab] = useState<"overview" | "analysis">(
    "overview"
  );

  // ---------------- Part 2 state (your existing table) ----------------
  const [limit, setLimit] = useState<number>(200);
  const [rows, setRows] = useState<FrequencyRow[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const apiHealthUrl = `${API_BASE}/api/v1/health`;
  const apiFreqUrl = `${API_BASE}/api/v1/frequency?limit=${limit}`;

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

  // ---------------- Part 3 state ----------------
  const [p3Freq, setP3Freq] = useState<Part3Row[]>([]);
  const [p3Stats, setP3Stats] = useState<Part3StatRow[]>([]);
  const [p3Loading, setP3Loading] = useState(false);
  const [p3Error, setP3Error] = useState<string | null>(null);

  const apiP3FreqUrl = `${API_BASE}/api/v1/part3/frequencies`;
  const apiP3StatsUrl = `${API_BASE}/api/v1/part3/stats`;

  // Fetch Part 3 data once (or whenever API_BASE changes)
  useEffect(() => {
    let cancelled = false;

    async function loadPart3() {
      setP3Loading(true);
      setP3Error(null);
      try {
        const [r1, r2] = await Promise.all([
          fetch(apiP3FreqUrl),
          fetch(apiP3StatsUrl),
        ]);

        if (!r1.ok) throw new Error(`Part3 frequencies error: ${r1.status}`);
        if (!r2.ok) throw new Error(`Part3 stats error: ${r2.status}`);

        const d1 = (await r1.json()) as Part3Row[];
        const d2 = (await r2.json()) as Part3StatRow[];

        if (!cancelled) {
          setP3Freq(d1);
          setP3Stats(d2);
        }
      } catch (e: any) {
        if (!cancelled) setP3Error(e?.message ?? "Unknown error");
      } finally {
        if (!cancelled) setP3Loading(false);
      }
    }

    loadPart3();
    return () => {
      cancelled = true;
    };
  }, [apiP3FreqUrl, apiP3StatsUrl]);

  const populations = useMemo(
    () => ["b_cell", "cd4_t_cell", "cd8_t_cell", "nk_cell", "monocyte"],
    []
  );

  const statsByPop = useMemo(() => {
    const m = new Map<string, Part3StatRow>();
    for (const s of p3Stats) m.set(s.population, s);
    return m;
  }, [p3Stats]);

  // --- box colors (high contrast on dark bg) ---
  const responderFill = "rgba(99, 102, 241, 0.45)"; // indigo
  const responderLine = "rgba(99, 102, 241, 1)";
  const nonResponderFill = "rgba(16, 185, 129, 0.40)"; // emerald
  const nonResponderLine = "rgba(16, 185, 129, 1)";

  function boxplotData(pop: string): ChartData<"boxplot", any, string> {
    const yes = p3Freq
      .filter((r) => r.population === pop && r.response === "yes")
      .map((r) => r.percentage);

    const no = p3Freq
      .filter((r) => r.population === pop && r.response === "no")
      .map((r) => r.percentage);

    return {
      labels: ["Responder", "Non-responder"],
      datasets: [
        {
          label: pop,
          // boxplot plugin expects arrays per category
          data: [yes, no],

          // Most important visual fix: per-box fill and border
          backgroundColor: [responderFill, nonResponderFill],
          borderColor: [responderLine, nonResponderLine],
          borderWidth: 2,

          // These are supported in many versions of chartjs-chart-boxplot.
          // If your current version ignores them, that's OK; the fill/border + axis fixes still work.
          medianColor: "#FFFFFF",
          whiskerColor: "rgba(229,231,235,0.9)",
          outlierColor: "rgba(244,63,94,0.95)",
          outlierRadius: 3,
        } as any,
      ],
    };
  }

  function plotTitle(pop: string) {
    const s = statsByPop.get(pop);
    if (!s) return pop;
    const p = fmtP(s.p_value);
    const q = s.q_value != null ? fmtP(s.q_value) : "NA";
    return `${pop}  (p=${p}, q=${q})`;
  }

  function boxOptions(pop: string): ChartOptions<"boxplot"> {
    return {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        title: {
          display: true,
          text: plotTitle(pop),
          color: "#E5E7EB",
          font: { weight: "700", size: 14 },
        },
        tooltip: {
          enabled: true,
          backgroundColor: "rgba(17,24,39,0.95)",
          titleColor: "#F9FAFB",
          bodyColor: "#E5E7EB",
          borderColor: "rgba(255,255,255,0.15)",
          borderWidth: 1,
        },
      },
      scales: {
        x: {
          ticks: { color: "#E5E7EB" },
          grid: { color: "rgba(255,255,255,0.08)" },
        },
        y: {
          title: {
            display: true,
            text: "Relative frequency (%)",
            color: "#E5E7EB",
            font: { weight: "700" },
          },
          ticks: { color: "#E5E7EB" },
          grid: { color: "rgba(255,255,255,0.08)" },
        },
      },
    };
  }

  return (
    <div style={{ maxWidth: 1100, margin: "0 auto", padding: 24 }}>
      <h1>Cell Counts Dashboard</h1>

      {/* API info always visible */}
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
      </div>

      {/* Tabs */}
      <div style={{ display: "flex", gap: 10, marginBottom: 16 }}>
        <button
          onClick={() => setActiveTab("overview")}
          style={pillStyle(activeTab === "overview")}
        >
          Data Overview
        </button>
        <button
          onClick={() => setActiveTab("analysis")}
          style={pillStyle(activeTab === "analysis")}
        >
          Analysis
        </button>
      </div>

      {/* ---------------- TAB: Data Overview (Part 2) ---------------- */}
      {activeTab === "overview" && (
        <>
          <div style={{ marginBottom: 8, fontWeight: 700 }}>
            Data Overview — Relative frequencies by sample/population
          </div>

          <div style={{ marginBottom: 12 }}>
            Frequency endpoint:{" "}
            <a href={apiFreqUrl} target="_blank" rel="noreferrer">
              {apiFreqUrl}
            </a>
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
            {error ? (
              <span style={{ color: "crimson" }}>Error: {error}</span>
            ) : null}
          </div>

          <div
            style={{
              border: "1px solid #ddd",
              borderRadius: 8,
              overflow: "auto",
            }}
          >
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr style={{ background: "#fafafa", color: "#111" }}>
                  <th
                    style={{
                      textAlign: "left",
                      padding: 10,
                      borderBottom: "1px solid #eee",
                      fontWeight: 700,
                    }}
                  >
                    sample
                  </th>
                  <th
                    style={{
                      textAlign: "right",
                      padding: 10,
                      borderBottom: "1px solid #eee",
                      fontWeight: 700,
                    }}
                  >
                    total_count
                  </th>
                  <th
                    style={{
                      textAlign: "left",
                      padding: 10,
                      borderBottom: "1px solid #eee",
                      fontWeight: 700,
                    }}
                  >
                    population
                  </th>
                  <th
                    style={{
                      textAlign: "right",
                      padding: 10,
                      borderBottom: "1px solid #eee",
                      fontWeight: 700,
                    }}
                  >
                    count
                  </th>
                  <th
                    style={{
                      textAlign: "right",
                      padding: 10,
                      borderBottom: "1px solid #eee",
                      fontWeight: 700,
                    }}
                  >
                    percentage
                  </th>
                </tr>
              </thead>
              <tbody>
                {filteredRows.map((r, idx) => (
                  <tr key={`${r.sample}-${r.population}-${idx}`}>
                    <td
                      style={{
                        padding: 10,
                        borderBottom: "1px solid #f2f2f2",
                      }}
                    >
                      {r.sample}
                    </td>
                    <td
                      style={{
                        padding: 10,
                        textAlign: "right",
                        borderBottom: "1px solid #f2f2f2",
                      }}
                    >
                      {fmtInt(r.total_count)}
                    </td>
                    <td
                      style={{
                        padding: 10,
                        borderBottom: "1px solid #f2f2f2",
                      }}
                    >
                      {r.population}
                    </td>
                    <td
                      style={{
                        padding: 10,
                        textAlign: "right",
                        borderBottom: "1px solid #f2f2f2",
                      }}
                    >
                      {fmtInt(r.count)}
                    </td>
                    <td
                      style={{
                        padding: 10,
                        textAlign: "right",
                        borderBottom: "1px solid #f2f2f2",
                      }}
                    >
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
        </>
      )}

      {/* ---------------- TAB: Analysis (Part 3) ---------------- */}
      {activeTab === "analysis" && (
        <>
          <div style={{ marginBottom: 8, fontWeight: 700 }}>
            Statistical Analysis — PBMC melanoma miraclib (responders vs
            non-responders)
          </div>

          <div style={{ marginBottom: 12 }}>
            Visual: boxplots of relative frequency (%) per immune population.
            Each plot title includes <b>p</b> and <b>q</b> (FDR).
          </div>

          <div style={{ marginBottom: 12 }}>
            Frequencies:{" "}
            <a href={apiP3FreqUrl} target="_blank" rel="noreferrer">
              {apiP3FreqUrl}
            </a>
            <br />
            Stats:{" "}
            <a href={apiP3StatsUrl} target="_blank" rel="noreferrer">
              {apiP3StatsUrl}
            </a>
          </div>

          {p3Loading ? <div>Loading analysis…</div> : null}
          {p3Error ? (
            <div style={{ color: "crimson" }}>Error: {p3Error}</div>
          ) : null}

          {/* Stats table */}
          {!p3Loading && !p3Error && p3Stats.length > 0 ? (
            <div
              style={{
                border: "1px solid #ddd",
                borderRadius: 8,
                overflow: "auto",
                marginBottom: 16,
              }}
            >
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr style={{ background: "#fafafa", color: "#111" }}>
                    <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #eee" }}>
                      population
                    </th>
                    <th style={{ textAlign: "right", padding: 10, borderBottom: "1px solid #eee" }}>
                      n_yes
                    </th>
                    <th style={{ textAlign: "right", padding: 10, borderBottom: "1px solid #eee" }}>
                      n_no
                    </th>
                    <th style={{ textAlign: "right", padding: 10, borderBottom: "1px solid #eee" }}>
                      median_yes (%)
                    </th>
                    <th style={{ textAlign: "right", padding: 10, borderBottom: "1px solid #eee" }}>
                      median_no (%)
                    </th>
                    <th style={{ textAlign: "right", padding: 10, borderBottom: "1px solid #eee" }}>
                      p_value
                    </th>
                    <th style={{ textAlign: "right", padding: 10, borderBottom: "1px solid #eee" }}>
                      q_value
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {p3Stats.map((s) => (
                    <tr key={s.population}>
                      <td style={{ padding: 10, borderBottom: "1px solid #f2f2f2" }}>
                        {s.population}
                      </td>
                      <td style={{ padding: 10, textAlign: "right", borderBottom: "1px solid #f2f2f2" }}>
                        {fmtInt(s.n_yes)}
                      </td>
                      <td style={{ padding: 10, textAlign: "right", borderBottom: "1px solid #f2f2f2" }}>
                        {fmtInt(s.n_no)}
                      </td>
                      <td style={{ padding: 10, textAlign: "right", borderBottom: "1px solid #f2f2f2" }}>
                        {s.median_yes.toFixed(3)}
                      </td>
                      <td style={{ padding: 10, textAlign: "right", borderBottom: "1px solid #f2f2f2" }}>
                        {s.median_no.toFixed(3)}
                      </td>
                      <td style={{ padding: 10, textAlign: "right", borderBottom: "1px solid #f2f2f2" }}>
                        {fmtP(s.p_value)}
                      </td>
                      <td style={{ padding: 10, textAlign: "right", borderBottom: "1px solid #f2f2f2" }}>
                        {s.q_value != null ? fmtP(s.q_value) : "NA"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : null}

          {/* Boxplots */}
          {!p3Loading && !p3Error ? (
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
                gap: 16,
              }}
            >
              {populations.map((pop) => (
                <div
                  key={pop}
                  style={{
                    border: "1px solid #ddd",
                    borderRadius: 8,
                    padding: 12,
                    background: "rgba(255,255,255,0.02)",
                  }}
                >
                  <Chart
                    type="boxplot"
                    data={boxplotData(pop)}
                    options={boxOptions(pop)}
                    height={260}
                  />
                </div>
              ))}
            </div>
          ) : null}

          {/* Simple legend */}
          <div style={{ marginTop: 14, display: "flex", gap: 14, alignItems: "center", flexWrap: "wrap" }}>
            <span style={{ display: "inline-flex", gap: 8, alignItems: "center" }}>
              <span style={{ width: 14, height: 14, borderRadius: 4, background: responderFill, border: `2px solid ${responderLine}` }} />
              Responder (yes)
            </span>
            <span style={{ display: "inline-flex", gap: 8, alignItems: "center" }}>
              <span style={{ width: 14, height: 14, borderRadius: 4, background: nonResponderFill, border: `2px solid ${nonResponderLine}` }} />
              Non-responder (no)
            </span>
          </div>
        </>
      )}
    </div>
  );
}