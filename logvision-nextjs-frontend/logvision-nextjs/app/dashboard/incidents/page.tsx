const rows = [
  { id: "INC-3091", status: "Open", sev: "Critical" },
  { id: "INC-3087", status: "Investigating", sev: "Warning" },
];

export default function IncidentsPage() {
  return <div className="space-y-6"><div><h1 className="text-xl font-bold">Incidents</h1><p className="mt-1 text-sm text-muted-foreground">Current incidents and triage status across services.</p></div><div className="glass-card animate-slide-up rounded-lg p-5"><table className="w-full text-sm"><thead className="text-left text-muted-foreground"><tr><th>ID</th><th>Status</th><th>Severity</th></tr></thead><tbody>{rows.map((r) => <tr key={r.id} className="border-t border-border/60"><td className="py-3">{r.id}</td><td>{r.status}</td><td>{r.sev}</td></tr>)}</tbody></table></div></div>;
}
