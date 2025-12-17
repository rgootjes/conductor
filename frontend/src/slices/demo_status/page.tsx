"use client";

import React, { useEffect, useState } from "react";

type DemoStatus = {
  status: string;
  environment: string;
  timestamp: string;
};

export function DemoStatusPage() {
  const [data, setData] = useState<DemoStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const controller = new AbortController();

    async function loadStatus() {
      try {
        const response = await fetch("/demo/status", { signal: controller.signal });

        if (!response.ok) {
          throw new Error(`Request failed with status ${response.status}`);
        }

        const payload: DemoStatus = await response.json();
        setData(payload);
      } catch (err) {
        if (err instanceof DOMException && err.name === "AbortError") return;
        setError((err as Error).message);
      } finally {
        setIsLoading(false);
      }
    }

    loadStatus();
    return () => controller.abort();
  }, []);

  return (
    <section style={{ border: "1px solid #e2e8f0", padding: "1.5rem", borderRadius: "0.75rem" }}>
      <h1 style={{ marginBottom: "0.5rem" }}>Demo Status</h1>
      <p style={{ color: "#475569", marginBottom: "1rem" }}>
        Live status for the demo environment, fetched directly from the backend slice.
      </p>

      {isLoading && <p>Loading status...</p>}
      {error && (
        <p role="alert" style={{ color: "#b91c1c" }}>
          Failed to load status: {error}
        </p>
      )}

      {data && !error && (
        <dl style={{ display: "grid", gridTemplateColumns: "max-content 1fr", gap: "0.5rem 1rem" }}>
          <dt style={{ fontWeight: 600 }}>Status</dt>
          <dd>{data.status}</dd>

          <dt style={{ fontWeight: 600 }}>Environment</dt>
          <dd>{data.environment}</dd>

          <dt style={{ fontWeight: 600 }}>Timestamp</dt>
          <dd>{new Date(data.timestamp).toLocaleString()}</dd>
        </dl>
      )}
    </section>
  );
}
