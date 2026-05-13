import { Gauge, Wrench, Clock3 } from "lucide-react";

export default function KibanaPage() {
  const url = process.env.NEXT_PUBLIC_KIBANA_DASHBOARD_URL || "";

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Gauge className="h-5 w-5 text-primary" />
        <div>
          <h1 className="text-xl font-bold">Kibana observability</h1>
          <p className="mt-1 text-sm text-muted-foreground">Visualisations avancees en cours de finalisation.</p>
        </div>
      </div>

      <div className="glass-card animate-slide-up rounded-xl border border-border/80 p-6">
        <div className="flex items-center gap-2 text-primary">
          <Wrench className="h-4 w-4" />
          <span className="text-sm font-semibold uppercase tracking-wider">Under Construction</span>
        </div>
        <h2 className="mt-3 text-lg font-semibold">Kibana Visualisations</h2>
        <p className="mt-2 max-w-2xl text-sm text-muted-foreground">
          Les dashboards Kibana de production seront affiches ici (erreurs, SLA, throughput, anomalies correlees).
          La logique de connexion est conservee, la couche visuelle finale est en cours.
        </p>

        <div className="mt-5 grid gap-4 md:grid-cols-3">
          <div className="rounded-lg border border-border bg-secondary/40 p-4">
            <p className="text-xs text-muted-foreground">Error Heatmap</p>
            <div className="mt-2 h-20 rounded-md bg-gradient-to-br from-primary/20 to-transparent" />
          </div>
          <div className="rounded-lg border border-border bg-secondary/40 p-4">
            <p className="text-xs text-muted-foreground">SLA Timeline</p>
            <div className="mt-2 h-20 rounded-md bg-gradient-to-r from-warning/20 to-transparent" />
          </div>
          <div className="rounded-lg border border-border bg-secondary/40 p-4">
            <p className="text-xs text-muted-foreground">Ingestion Flow</p>
            <div className="mt-2 h-20 rounded-md bg-gradient-to-r from-success/20 to-transparent" />
          </div>
        </div>

        {url ? (
          <p className="mt-5 inline-flex items-center gap-2 text-xs text-muted-foreground">
            <Clock3 className="h-3.5 w-3.5" />
            URL Kibana detectee. L iframe sera reactivee apres finalisation visuelle.
          </p>
        ) : (
          <p className="mt-5 text-xs text-muted-foreground">Ajoutez NEXT_PUBLIC_KIBANA_DASHBOARD_URL pour activer la source des dashboards.</p>
        )}
      </div>
    </div>
  );
}
