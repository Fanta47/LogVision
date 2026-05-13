import { Brain, Wrench } from "lucide-react";

export default function PredictionsPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Brain className="h-5 w-5 text-primary" />
        <div>
          <h1 className="text-xl font-bold">Incident predictions</h1>
          <p className="mt-1 text-sm text-muted-foreground">Previsions intelligentes en cours de deploiement.</p>
        </div>
      </div>

      <div className="glass-card animate-slide-up rounded-xl border border-border/80 p-6">
        <div className="flex items-center gap-2 text-primary">
          <Wrench className="h-4 w-4" />
          <span className="text-sm font-semibold uppercase tracking-wider">Under Construction</span>
        </div>
        <h2 className="mt-3 text-lg font-semibold">Predictive Visualisations</h2>
        <p className="mt-2 text-sm text-muted-foreground">
          Cette zone affichera la probabilite d incident, la fenetre de risque et les facteurs explicatifs
          par application et composant.
        </p>

        <div className="mt-5 grid gap-4 md:grid-cols-3">
          <div className="rounded-lg border border-border bg-secondary/40 p-4">
            <p className="text-xs text-muted-foreground">Risk Score</p>
            <div className="mt-2 h-16 rounded-md bg-gradient-to-r from-primary/25 to-transparent" />
          </div>
          <div className="rounded-lg border border-border bg-secondary/40 p-4">
            <p className="text-xs text-muted-foreground">Trend Forecast</p>
            <div className="mt-2 h-16 rounded-md bg-gradient-to-r from-warning/25 to-transparent" />
          </div>
          <div className="rounded-lg border border-border bg-secondary/40 p-4">
            <p className="text-xs text-muted-foreground">Top Drivers</p>
            <div className="mt-2 h-16 rounded-md bg-gradient-to-r from-success/25 to-transparent" />
          </div>
        </div>
      </div>
    </div>
  );
}
