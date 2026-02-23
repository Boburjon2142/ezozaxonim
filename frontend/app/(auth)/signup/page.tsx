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

export default function SignupPage() {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const setTokens = useAuthStore((s) => s.setTokens);
  const router = useRouter();

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const data = await api<TokenResponse>("/api/v1/auth/signup", { method: "POST", body: JSON.stringify({ full_name: fullName, email, password }) });
      setTokens(data.access_token, data.refresh_token);
      router.push("/today");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Signup failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto max-w-md p-6">
      <form onSubmit={onSubmit} className="surface space-y-4 p-6">
        <h1 className="text-2xl font-bold">Create account</h1>
        <Input placeholder="Full name" value={fullName} onChange={(e) => setFullName(e.target.value)} />
        <Input placeholder="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
        <Input placeholder="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        <Button disabled={loading}>{loading ? "Creating..." : "Start Free"}</Button>
        <p className="text-sm text-black/70">Already have an account? <Link className="underline" href="/login">Sign in</Link></p>
      </form>
    </main>
  );
}
