"use client";
import { useEffect, useState } from "react";
import { Brain, Play, Wrench } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/Button";
import { getModelComparison, runMLScoring } from "@/lib/api";

export default function ModelsPage() {
  const [rows, setRows] = useState<any[]>([]);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    getModelComparison().then(setRows).catch(() => setRows([]));
  }, []);

  async function run() {
    setRunning(true);
    try {
      const res = await runMLScoring();
      toast.success(res.message || "ML scoring started");
      getModelComparison().then(setRows).catch(() => setRows([]));
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "ML scoring failed");
    } finally {
      setRunning(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Brain className="h-5 w-5 text-primary" />
          <div>
            <h1 className="text-xl font-bold">ML models</h1>
            <p className="mt-1 text-sm text-muted-foreground">Visualisations ML en cours de construction.</p>
          </div>
        </div>
        <Button onClick={run} disabled={running}>
          <Play className="mr-2 h-4 w-4" />
          {running ? "Running..." : "Run scoring"}
        </Button>
      </div>

      <div className="glass-card animate-slide-up rounded-xl border border-border/80 p-6">
        <div className="flex items-center gap-2 text-primary">
          <Wrench className="h-4 w-4" />
          <span className="text-sm font-semibold uppercase tracking-wider">Under Construction</span>
        </div>
        <h2 className="mt-3 text-lg font-semibold">ML Visual Analytics</h2>
        <p className="mt-2 text-sm text-muted-foreground">
          Les courbes SHAP, matrices de confusion, distribution des scores et comparaison multi-modeles arrivent ici dans la prochaine iteration.
        </p>
      </div>

      <div className="glass-card rounded-lg p-5">
        <h2 className="mb-3 text-sm font-semibold">Model comparison (data active)</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="text-xs uppercase text-muted-foreground">
              <tr>
                <th className="py-2">Sequence</th>
                <th>App</th>
                <th>Component</th>
                <th>IForest</th>
                <th>KMeans</th>
                <th>LogBERT</th>
                <th>Final</th>
                <th>Label</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.sequence_uid} className="border-t border-border">
                  <td className="py-3 font-mono text-xs">{String(r.sequence_uid).slice(0, 16)}</td>
                  <td>{r.application_key}</td>
                  <td>{r.component_name}</td>
                  <td>{Number(r.iforest_anomaly_score ?? 0).toFixed(3)}</td>
                  <td>{Number(r.kmeans_anomaly_score ?? 0).toFixed(3)}</td>
                  <td>{Number(r.logbert_like_score ?? 0).toFixed(3)}</td>
                  <td>{Number(r.final_anomaly_score ?? 0).toFixed(3)}</td>
                  <td>{r.final_anomaly_label}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {rows.length === 0 && <p className="py-8 text-center text-sm text-muted-foreground">No model comparison output yet.</p>}
        </div>
      </div>
    </div>
  );
}
