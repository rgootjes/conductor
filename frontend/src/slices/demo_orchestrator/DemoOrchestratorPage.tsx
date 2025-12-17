"use client";

import React, { useEffect, useRef, useState } from "react";

type DemoRunStep = {
  agent: "planner" | "designer" | "builder";
  status: "pending" | "running" | "completed";
  output: string | null;
};

type DemoRunStatus = {
  run_id: string;
  status: "pending" | "running" | "completed";
  current_agent: string | null;
  steps: DemoRunStep[];
};

function StepBadge({ status }: { status: DemoRunStep["status"] }) {
  const colors: Record<DemoRunStep["status"], string> = {
    pending: "#cbd5e1",
    running: "#f59e0b",
    completed: "#22c55e",
  };

  return (
    <span
      style={{
        display: "inline-block",
        padding: "0.1rem 0.5rem",
        borderRadius: "9999px",
        background: colors[status],
        color: "#0f172a",
        fontSize: "0.75rem",
        fontWeight: 600,
      }}
    >
      {status}
    </span>
  );
}

export function DemoOrchestratorPage() {
  const [runId, setRunId] = useState<string | null>(null);
  const [runData, setRunData] = useState<DemoRunStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isStarting, setIsStarting] = useState(false);
  const pollRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (!runId) return undefined;

    const controller = new AbortController();

    const poll = async () => {
      try {
        const response = await fetch(`/api/demo/run/${runId}`, {
          cache: "no-store",
          signal: controller.signal,
        });

        if (!response.ok) {
          throw new Error(`Request failed with status ${response.status}`);
        }

        const payload: DemoRunStatus = await response.json();
        setRunData(payload);

        if (payload.status === "completed" && pollRef.current) {
          clearInterval(pollRef.current);
          pollRef.current = null;
        }
      } catch (err) {
        if (err instanceof DOMException && err.name === "AbortError") return;
        setError((err as Error).message);
        if (pollRef.current) {
          clearInterval(pollRef.current);
          pollRef.current = null;
        }
      }
    };

    poll();
    pollRef.current = setInterval(poll, 1000);

    return () => {
      controller.abort();
      if (pollRef.current) {
        clearInterval(pollRef.current);
        pollRef.current = null;
      }
    };
  }, [runId]);

  const startDemo = async () => {
    setIsStarting(true);
    setError(null);
    setRunData(null);

    try {
      const response = await fetch("/api/demo/run", { method: "POST" });
      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
      }

      const payload: { run_id: string } = await response.json();
      setRunId(payload.run_id);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setIsStarting(false);
    }
  };

  const currentStatus = runData?.status ?? "pending";
  const currentAgent = runData?.current_agent ?? "None";

  return (
    <section style={{ border: "1px solid #e2e8f0", padding: "1.5rem", borderRadius: "0.75rem" }}>
      <h1 style={{ marginBottom: "0.5rem" }}>Demo Orchestrator</h1>
      <p style={{ color: "#475569", marginBottom: "1rem" }}>
        Start a simulated run to watch planner, designer, and builder agents execute in sequence.
      </p>

      <div style={{ display: "flex", gap: "0.75rem", alignItems: "center", marginBottom: "1rem" }}>
        <button
          type="button"
          onClick={startDemo}
          disabled={isStarting || currentStatus === "running"}
          style={{
            padding: "0.5rem 1rem",
            background: "#0ea5e9",
            color: "white",
            border: "none",
            borderRadius: "0.5rem",
            cursor: isStarting || currentStatus === "running" ? "not-allowed" : "pointer",
          }}
        >
          {isStarting ? "Starting..." : "Start Demo"}
        </button>
        <div style={{ fontSize: "0.9rem", color: "#0f172a" }}>
          <strong>Status:</strong> {runId ? <StepBadge status={currentStatus as DemoRunStep["status"]} /> : "Idle"}
        </div>
        <div style={{ fontSize: "0.9rem", color: "#0f172a" }}>
          <strong>Current Agent:</strong> {runId ? currentAgent : "None"}
        </div>
      </div>

      {error && (
        <p role="alert" style={{ color: "#b91c1c", marginBottom: "1rem" }}>
          Failed to run demo: {error}
        </p>
      )}

      {runData && (
        <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
          {runData.steps.map((step) => (
            <div
              key={step.agent}
              style={{
                border: "1px solid #e2e8f0",
                borderRadius: "0.5rem",
                padding: "0.75rem",
                background: "#f8fafc",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <strong style={{ textTransform: "capitalize" }}>{step.agent}</strong>
                <StepBadge status={step.status} />
              </div>
              <p style={{ marginTop: "0.5rem", color: "#334155" }}>
                {step.output ?? "Awaiting output..."}
              </p>
            </div>
          ))}
        </div>
      )}

      {!runData && !error && !isStarting && (
        <p style={{ color: "#475569" }}>Click "Start Demo" to launch the mock orchestrator.</p>
      )}
    </section>
  );
}
