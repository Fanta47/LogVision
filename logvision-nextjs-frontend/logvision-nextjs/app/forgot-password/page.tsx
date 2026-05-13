import Link from "next/link";
import { VermegAnimatedLogo } from "@/components/VermegAnimatedLogo";
import { LoginBackground } from "@/components/LoginBackground";

export default function ForgotPasswordPage() {
  return <div className="login-bg relative flex min-h-screen items-center justify-center overflow-hidden px-4"><LoginBackground /><div className="glass-card relative z-10 w-full max-w-md rounded-2xl p-8"><div className="mb-6 flex flex-col items-center gap-4"><VermegAnimatedLogo size="md" /><h1 className="text-xl font-semibold">Forgot Password</h1></div><p className="text-sm text-muted-foreground">Contact your administrator to reset access in this demo build.</p><Link href="/login" className="mt-6 inline-flex rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground">Back to login</Link></div></div>;
}
