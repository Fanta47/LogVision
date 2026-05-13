import { Shield, Wrench } from "lucide-react";

const roles = [
  { name: "admin", perms: "system, users, config" },
  { name: "manager", perms: "reports, predictions, incidents" },
  { name: "user", perms: "ingest, logs, anomalies" },
];

export default function AdminRolesPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Shield className="h-5 w-5 text-primary" />
        <div>
          <h1 className="text-xl font-bold">Admin Roles</h1>
          <p className="mt-1 text-sm text-muted-foreground">Matrice des permissions par role.</p>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        {roles.map((r) => (
          <div key={r.name} className="glass-card animate-slide-up rounded-lg p-5">
            <h2 className="text-base font-semibold uppercase">{r.name}</h2>
            <p className="mt-2 text-xs text-muted-foreground">{r.perms}</p>
          </div>
        ))}
      </div>

      <div className="glass-card rounded-lg p-5">
        <div className="flex items-center gap-2 text-primary">
          <Wrench className="h-4 w-4" />
          <span className="text-sm font-semibold uppercase tracking-wider">Under Construction</span>
        </div>
        <p className="mt-2 text-sm text-muted-foreground">Editeur dynamique RBAC et heritage de permissions bientot disponibles.</p>
      </div>
    </div>
  );
}
