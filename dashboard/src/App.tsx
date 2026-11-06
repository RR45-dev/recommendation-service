import React, { useEffect, useState } from "react";

const API_BASE = process.env.REACT_APP_SERVING_API || "http://localhost:5000";

interface Metric { metric_name: string; metric_value: number; computed_at: string }
interface Recommendation { item_id: number; score: number; rank: number }
interface SimilarItem { similar_item_id: number; similarity: number; rank: number }

export default function App() {
  const [metrics, setMetrics] = useState<Metric[]>([]);
  const [userId, setUserId] = useState("1");
  const [recs, setRecs] = useState<Recommendation[]>([]);
  const [itemId, setItemId] = useState("1");
  const [similar, setSimilar] = useState<SimilarItem[]>([]);

  useEffect(() => {
    fetch(`${API_BASE}/api/metrics`).then((r) => r.json()).then(setMetrics).catch(() => {});
  }, []);

  const lookupUser = async () => {
    const res = await fetch(`${API_BASE}/api/recommendations/${userId}`);
    const data = await res.json();
    setRecs(data.recommendations || []);
  };

  const lookupItem = async () => {
    const res = await fetch(`${API_BASE}/api/items/${itemId}/similar`);
    const data = await res.json();
    setSimilar(data.similarItems || []);
  };

  return (
    <div style={{ fontFamily: "sans-serif", maxWidth: 800, margin: "40px auto" }}>
      <h1>Recommendation Admin</h1>

      <h2>Model quality metrics (last training run)</h2>
      <table border={1} cellPadding={6} style={{ borderCollapse: "collapse", width: "100%" }}>
        <thead><tr><th>Metric</th><th>Value</th><th>Computed at</th></tr></thead>
        <tbody>
          {metrics.map((m) => (
            <tr key={m.metric_name}>
              <td>{m.metric_name}</td>
              <td>{m.metric_value.toFixed(4)}</td>
              <td>{new Date(m.computed_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2>Recommendations for a user</h2>
      <input value={userId} onChange={(e) => setUserId(e.target.value)} placeholder="User ID" />
      <button onClick={lookupUser}>Look up</button>
      <ul>{recs.map((r) => <li key={r.rank}>#{r.rank + 1}: item {r.item_id} (score {r.score.toFixed(3)})</li>)}</ul>

      <h2>Items similar to an item</h2>
      <input value={itemId} onChange={(e) => setItemId(e.target.value)} placeholder="Item ID" />
      <button onClick={lookupItem}>Look up</button>
      <ul>{similar.map((s) => <li key={s.rank}>#{s.rank + 1}: item {s.similar_item_id} (similarity {s.similarity.toFixed(3)})</li>)}</ul>
    </div>
  );
}
