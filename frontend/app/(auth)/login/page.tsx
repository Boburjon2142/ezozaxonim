"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { TokenResponse } from "@/lib/types";
import { useAuthStore } from "@/store/auth";
import { useRouter } from "next/navigation";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const setTokens = useAuthStore((s) => s.setTokens);
  const router = useRouter();

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const data = await api<TokenResponse>("/api/v1/auth/login", { method: "POST", body: JSON.stringify({ email, password }) });
      setTokens(data.access_token, data.refresh_token);
      router.push("/today");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto max-w-md p-6">
      <form onSubmit={onSubmit} className="surface space-y-4 p-6">
        <h1 className="text-2xl font-bold">Sign in</h1>
        <Input placeholder="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
        <Input placeholder="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        <Button disabled={loading}>{loading ? "Signing in..." : "Sign In"}</Button>
        <p className="text-sm text-black/70">No account? <Link className="underline" href="/signup">Create one</Link></p>
      </form>
    </main>
  );
}
