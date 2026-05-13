import { Users, Wrench } from "lucide-react";

const users = [
  { name: "Admin User", role: "admin" },
  { name: "Manager User", role: "manager" },
  { name: "Analyst User", role: "user" },
];

export default function AdminUsersPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Users className="h-5 w-5 text-primary" />
        <div>
          <h1 className="text-xl font-bold">Admin Users</h1>
          <p className="mt-1 text-sm text-muted-foreground">Gestion des utilisateurs et acces.</p>
        </div>
      </div>

      <div className="glass-card rounded-lg p-5">
        <table className="w-full text-left text-sm">
          <thead className="text-xs uppercase text-muted-foreground">
            <tr>
              <th className="py-2">Name</th>
              <th>Role</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.name} className="border-t border-border">
                <td className="py-3">{u.name}</td>
                <td className="uppercase">{u.role}</td>
                <td>Active</td>
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
        <p className="mt-2 text-sm text-muted-foreground">Provisioning SSO, invitations et audit trails seront branches ici.</p>
      </div>
    </div>
  );
}
