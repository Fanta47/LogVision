export type Role = "user" | "manager" | "admin";
export type SessionUser = { name: string; email: string; role: Role; initials: string; };
const KEY = "logvision_session";
export function roleFromEmail(email: string): Role {
  if (email.includes("admin")) return "admin";
  if (email.includes("manager")) return "manager";
  return "user";
}
export function login(email: string, _password: string): SessionUser {
  const role = roleFromEmail(email);
  const user: SessionUser = { email, role, name: role === "admin" ? "Admin User" : role === "manager" ? "Manager User" : "Analyst User", initials: role === "admin" ? "AD" : role === "manager" ? "MG" : "AN" };
  localStorage.setItem(KEY, JSON.stringify(user));
  localStorage.setItem("logvision_token", "dev-token");
  return user;
}
export function getSession(): SessionUser | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem(KEY);
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw) as SessionUser;
    if (!parsed?.email || !parsed?.role) return null;
    return parsed;
  } catch {
    localStorage.removeItem(KEY);
    localStorage.removeItem("logvision_token");
    return null;
  }
}
export function logout() { localStorage.removeItem(KEY); localStorage.removeItem("logvision_token"); }
export function roleLabel(role: Role) { return role === "admin" ? "Administrator" : role === "manager" ? "Manager" : "Analyst"; }
