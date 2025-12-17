"use client";

import React, { useEffect, useRef, useState } from "react";

type WorkflowInput = {
  name: string;
  description?: string;
  required?: boolean;
  example?: string | null;
};

type WorkflowStepDefinition = {
  id: string;
  name?: string;
  agent: string;
  input: string;
};

type WorkflowDefinition = {
  version: string | number;
  name: string;
  description: string;
  inputs: WorkflowInput[];
  agents: { name: string; kind: string }[];
  steps: WorkflowStepDefinition[];
};

type WorkflowRunStep = {
  id: string;
  agent: string;
  input: string | null;
  output: string | null;
  status: "pending" | "running" | "completed" | "failed";
};

type WorkflowRunStatus = {
  run_id: string;
  workflow_name: string;
  status: "pending" | "running" | "completed" | "failed";
  current_step: string | null;
  steps: WorkflowRunStep[];
  error: string | null;
};

type Props = {
  workflowName?: string;
};

function StepBadge({ status }: { status: WorkflowRunStep["status"] }) {
  const colors: Record<WorkflowRunStep["status"], string> = {
    pending: "#cbd5e1",
    running: "#f59e0b",
    completed: "#22c55e",
    failed: "#ef4444",
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

export function WorkflowOrchestratorPage({ workflowName = "demo_linear" }: Props) {
  const [definition, setDefinition] = useState<WorkflowDefinition | null>(null);
  const [inputs, setInputs] = useState<Record<string, string>>({});
  const [runId, setRunId] = useState<string | null>(null);
  const [runStatus, setRunStatus] = useState<WorkflowRunStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const pollRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    const fetchDefinition = async () => {
      try {
        const response = await fetch(`/api/workflow/definition/${workflowName}`);
        if (!response.ok) {
          throw new Error(`Failed to load workflow definition (${response.status})`);
        }

        const payload: WorkflowDefinition = await response.json();
        setDefinition(payload);
        const defaults: Record<string, string> = {};
        payload.inputs.forEach((input) => {
          defaults[input.name] = input.example ?? "";
        });
        setInputs(defaults);
      } catch (err) {
        setError((err as Error).message);
      }
    };

    fetchDefinition();
  }, [workflowName]);

  useEffect(() => {
    if (!runId) return undefined;

    const controller = new AbortController();

    const poll = async () => {
      try {
        const response = await fetch(`/api/workflow/run/${runId}`, {
          cache: "no-store",
          signal: controller.signal,
        });

        if (!response.ok) {
          throw new Error(`Status request failed (${response.status})`);
        }

        const payload: WorkflowRunStatus = await response.json();
        setRunStatus(payload);

        if ((payload.status === "completed" || payload.status === "failed") && pollRef.current) {
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
    pollRef.current = setInterval(poll, 1200);

    return () => {
      controller.abort();
      if (pollRef.current) {
        clearInterval(pollRef.current);
        pollRef.current = null;
      }
    };
  }, [runId]);

  const handleInputChange = (name: string, value: string) => {
    setInputs((prev) => ({ ...prev, [name]: value }));
  };

  const startRun = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!definition) return;

    setIsSubmitting(true);
    setError(null);
    setRunStatus(null);

    try {
      const response = await fetch(`/api/workflow/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ workflow_name: definition.name, inputs }),
      });

      if (!response.ok) {
        throw new Error(`Run request failed (${response.status})`);
      }

      const payload: { run_id: string } = await response.json();
      setRunId(payload.run_id);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const currentStatus = runStatus?.status ?? "pending";
  const currentStep = runStatus?.current_step ?? "None";

  return (
    <section style={{ border: "1px solid #e2e8f0", padding: "1.5rem", borderRadius: "0.75rem" }}>
      <h1 style={{ marginBottom: "0.25rem" }}>Workflow Orchestrator</h1>
      <p style={{ color: "#475569", marginBottom: "0.75rem" }}>
        YAML-defined workflow executed by mock agents. All steps run in sequence with live polling.
      </p>

      {definition && (
        <div style={{ marginBottom: "1rem" }}>
          <strong style={{ display: "block", fontSize: "1rem" }}>{definition.name}</strong>
          <span style={{ color: "#334155", fontSize: "0.95rem" }}>{definition.description}</span>
        </div>
      )}

      <form onSubmit={startRun} style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
        {definition?.inputs.map((input) => (
          <label key={input.name} style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
            <span style={{ fontWeight: 600, color: "#0f172a" }}>
              {input.name} {input.required === false ? "(optional)" : ""}
            </span>
            <input
              type="text"
              name={input.name}
              required={input.required !== false}
              placeholder={input.description ?? ""}
              value={inputs[input.name] ?? ""}
              onChange={(event) => handleInputChange(input.name, event.target.value)}
              style={{
                padding: "0.5rem 0.75rem",
                borderRadius: "0.5rem",
                border: "1px solid #cbd5e1",
              }}
            />
            {input.description && <span style={{ color: "#64748b", fontSize: "0.9rem" }}>{input.description}</span>}
          </label>
        ))}

        <button
          type="submit"
          disabled={isSubmitting || currentStatus === "running"}
          style={{
            padding: "0.5rem 1rem",
            background: "#0ea5e9",
            color: "white",
            border: "none",
            borderRadius: "0.5rem",
            cursor: isSubmitting || currentStatus === "running" ? "not-allowed" : "pointer",
            fontWeight: 600,
          }}
        >
          {isSubmitting ? "Starting..." : "Run Workflow"}
        </button>
      </form>

      <div style={{ display: "flex", gap: "1rem", alignItems: "center", marginTop: "1rem" }}>
        <div>
          <strong>Status:</strong> {runId ? <StepBadge status={currentStatus as WorkflowRunStep["status"]} /> : "Idle"}
        </div>
        <div>
          <strong>Current step:</strong> {runId ? currentStep : "None"}
        </div>
      </div>

      {error && (
        <p role="alert" style={{ color: "#b91c1c", marginTop: "0.75rem" }}>
          {error}
        </p>
      )}

      {runStatus && (
        <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem", marginTop: "1rem" }}>
          {runStatus.steps.map((step) => (
            <div
              key={step.id}
              style={{
                border: "1px solid #e2e8f0",
                borderRadius: "0.5rem",
                padding: "0.75rem",
                background: "#f8fafc",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div>
                  <strong>{definition?.steps.find((candidate) => candidate.id === step.id)?.name ?? step.id}</strong>{" "}
                  <span style={{ color: "#475569" }}>({step.agent})</span>
                </div>
                <StepBadge status={step.status} />
              </div>
              <p style={{ marginTop: "0.4rem", color: "#0f172a" }}>
                <strong>Input:</strong> {step.input ?? "Pending"}
              </p>
              <p style={{ marginTop: "0.3rem", color: "#334155" }}>
                <strong>Output:</strong> {step.output ?? "Waiting for agent output..."}
              </p>
            </div>
          ))}
        </div>
      )}

      {!runStatus && !error && <p style={{ color: "#64748b", marginTop: "0.75rem" }}>Provide inputs to run the workflow.</p>}
    </section>
  );
}
