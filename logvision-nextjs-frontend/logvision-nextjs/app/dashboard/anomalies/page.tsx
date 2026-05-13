"use client";
import { useEffect, useState } from "react";
import { Brain, Search, TrendingUp, Zap } from "lucide-react";
import { getAnomalies, AnomalyItem } from "@/lib/api";

const fallback: AnomalyItem[] = [
  {
    sequence_uid: "demo-sql-burst",
    application_key: "MegaCustody",
    component_name: "Persistence",
    start_timestamp: "-",
    end_timestamp: "-",
    anomaly_score: 0.91,
    anomaly_label: "anomalous",
    model_name: "ensemble_logbert_like",
    model_version: "v1",
  },
  {
    sequence_uid: "demo-sla-not-found",
    application_key: "MegaCustody",
    component_name: "MegaCustodySLALogger",
    start_timestamp: "-",
    end_timestamp: "-",
    anomaly_score: 0.84,
    anomaly_label: "anomalous",
    model_name: "ensemble_logbert_like",
    model_version: "v1",
  },
];

function badge(label: string, score: number) {
  if (score >= 0.7 || label === "anomalous") return "bg-critical/15 text-critical";
  if (score >= 0.3) return "bg-warning/15 text-warning";
  return "bg-success/15 text-success";
}

export default function AnomaliesPage() {
  const [items, setItems] = useState<AnomalyItem[]>([]);

  useEffect(() => {
    getAnomalies().then(setItems).catch(() => setItems(fallback));
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Search className="h-5 w-5 text-primary" />
        <div>
          <h1 className="text-xl font-bold">Anomaly explorer</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Sequences scored by Isolation Forest, K-means and LogBERT-like embeddings.
          </p>
        </div>
      </div>

      <div className="space-y-3">
        {items.map((a) => (
          <div key={a.sequence_uid} className="glass-card animate-slide-up rounded-lg p-5">
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <Zap className="h-4 w-4 text-warning" />
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs text-muted-foreground">{a.sequence_uid.slice(0, 20)}</span>
                    <span className={`rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase ${badge(a.anomaly_label, a.anomaly_score)}`}>
                      {a.anomaly_label}
                    </span>
                  </div>
                  <h3 className="mt-1 text-sm font-semibold">{a.application_key} / {a.component_name}</h3>
                  <p className="text-xs text-muted-foreground">
                    {a.start_timestamp} {"->"} {a.end_timestamp}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-1 text-xs text-muted-foreground">
                <TrendingUp className="h-3 w-3" />
                <span>{a.anomaly_score.toFixed(3)}</span>
              </div>
            </div>

            <div className="mt-3 flex items-start gap-2 rounded-md bg-primary/5 p-3">
              <Brain className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
              <div>
                <p className="text-[10px] font-semibold uppercase tracking-wider text-primary">ML Analysis</p>
                <p className="mt-1 text-xs leading-relaxed text-muted-foreground">
                  High scores indicate rare sequence behavior. For Persistence, inspect SQL bursts, missing Result Size events,
                  long queries and repeated same-thread activity. For SLA, inspect NOT FOUND frequency and repeated contexts.
                </p>
                <p className="mt-1 text-[10px] text-muted-foreground">
                  Model: {a.model_name ?? "-"}:{a.model_version ?? "-"}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
