import { Settings2, Wrench } from "lucide-react";

export default function AdminConfigPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Settings2 className="h-5 w-5 text-primary" />
        <div>
          <h1 className="text-xl font-bold">Admin Config</h1>
          <p className="mt-1 text-sm text-muted-foreground">Parametres plateforme et integrations.</p>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <div className="glass-card rounded-lg p-5">
          <h2 className="font-medium">Elasticsearch</h2>
          <p className="mt-2 text-sm text-muted-foreground">Index pattern, retention, snapshot policy.</p>
        </div>
        <div className="glass-card rounded-lg p-5">
          <h2 className="font-medium">PostgreSQL</h2>
          <p className="mt-2 text-sm text-muted-foreground">ETL watermark, vacuum windows, analytics schema.</p>
        </div>
      </div>

      <div className="glass-card rounded-lg p-5">
        <div className="flex items-center gap-2 text-primary">
          <Wrench className="h-4 w-4" />
          <span className="text-sm font-semibold uppercase tracking-wider">Under Construction</span>
        </div>
        <p className="mt-2 text-sm text-muted-foreground">UI d edition de configuration securisee avec validation et historique bientot disponible.</p>
      </div>
    </div>
  );
}
