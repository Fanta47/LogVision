export default function ReportsPage() {
  return <div className="space-y-6"><div><h1 className="text-xl font-bold">Reports</h1><p className="mt-1 text-sm text-muted-foreground">Generate weekly anomaly and SLA reporting bundles.</p></div><div className="glass-card animate-slide-up rounded-lg p-5"><p className="text-sm text-muted-foreground">Generate weekly anomaly and SLA reports.</p><button className="mt-4 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground">Export PDF</button></div></div>;
}
