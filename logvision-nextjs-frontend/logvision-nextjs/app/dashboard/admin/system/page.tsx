import { Server, Activity } from "lucide-react";

const systems = [
  { name: "Elasticsearch", status: "Healthy", cls: "status-dot-success" },
  { name: "PostgreSQL", status: "Healthy", cls: "status-dot-success" },
  { name: "ETL Service", status: "Running", cls: "status-dot-warning" },
  { name: "ML Service", status: "Under review", cls: "status-dot-warning" },
];

export default function AdminSystemPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Server className="h-5 w-5 text-primary" />
        <div>
          <h1 className="text-xl font-bold">Admin System</h1>
          <p className="mt-1 text-sm text-muted-foreground">Observabilite des services critiques LogVision.</p>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {systems.map((s) => (
          <div key={s.name} className="glass-card animate-slide-up rounded-lg p-5">
            <div className="flex items-center justify-between">
              <h2 className="font-medium">{s.name}</h2>
              <span className={`status-dot ${s.cls} animate-pulse-glow`} />
            </div>
            <p className="mt-2 text-sm text-muted-foreground">{s.status}</p>
          </div>
        ))}
      </div>

      <div className="glass-card rounded-lg p-5">
        <div className="flex items-center gap-2 text-primary">
          <Activity className="h-4 w-4" />
          <span className="text-sm font-semibold uppercase tracking-wider">Under Construction</span>
        </div>
        <p className="mt-2 text-sm text-muted-foreground">Les diagnostics avances seront ajoutes ici (latence, saturation, health timeline).</p>
      </div>
    </div>
  );
}
