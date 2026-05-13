import { Bell, Wrench } from "lucide-react";

const rules = [
  { name: "Critical Error Burst", state: "Enabled" },
  { name: "SLA Timeout", state: "Enabled" },
  { name: "Auth Failure Spike", state: "Disabled" },
];

export default function AdminAlertsPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Bell className="h-5 w-5 text-primary" />
        <div>
          <h1 className="text-xl font-bold">Admin Alert Rules</h1>
          <p className="mt-1 text-sm text-muted-foreground">Regles de detection et notifications.</p>
        </div>
      </div>

      <div className="glass-card rounded-lg p-5">
        <table className="w-full text-left text-sm">
          <thead className="text-xs uppercase text-muted-foreground">
            <tr>
              <th className="py-2">Rule</th>
              <th>State</th>
            </tr>
          </thead>
          <tbody>
            {rules.map((r) => (
              <tr key={r.name} className="border-t border-border">
                <td className="py-3">{r.name}</td>
                <td>{r.state}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="glass-card rounded-lg p-5">
        <div className="flex items-center gap-2 text-primary">
          <Wrench className="h-4 w-4" />
          <span className="text-sm font-semibold uppercase tracking-wider">Under Construction</span>
        </div>
        <p className="mt-2 text-sm text-muted-foreground">Canaux Teams, Slack, Email et strategies d escalation seront ajoutes.</p>
      </div>
    </div>
  );
}
