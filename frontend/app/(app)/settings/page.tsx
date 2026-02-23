"use client";

import { FormEvent, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useAuthStore } from "@/store/auth";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

type BreakRule = {
  focus_min: number;
  break_min: number;
  long_break_min: number;
  long_break_every: number;
  adaptive_enabled: boolean;
};

export default function SettingsPage() {
  const token = useAuthStore((s) => s.accessToken);
  const { data, refetch } = useQuery({
    queryKey: ["break-rule"],
    queryFn: () => api<BreakRule>("/api/v1/settings/break-rule", {}, token || undefined),
    enabled: !!token,
  });
  const [focus, setFocus] = useState(25);
  const [rest, setRest] = useState(5);

  async function save(e: FormEvent) {
    e.preventDefault();
    if (!token) return;
    await api("/api/v1/settings/break-rule", { method: "PUT", body: JSON.stringify({ focus_min: focus, break_min: rest, long_break_min: 15, long_break_every: 4, adaptive_enabled: true }) }, token);
    await refetch();
  }

  return (
    <>
      <h1 className="text-2xl font-bold">Settings</h1>
      <Card>
        <form className="grid gap-2 md:grid-cols-3" onSubmit={save}>
          <Input type="number" defaultValue={data?.focus_min ?? 25} onChange={(e) => setFocus(Number(e.target.value))} />
          <Input type="number" defaultValue={data?.break_min ?? 5} onChange={(e) => setRest(Number(e.target.value))} />
          <Button>Save Break Rule</Button>
        </form>
      </Card>
    </>
  );
}
