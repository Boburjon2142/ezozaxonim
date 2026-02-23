"use client";

import { FormEvent, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useAuthStore } from "@/store/auth";
import { Plan } from "@/lib/types";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { EmptyState } from "@/components/features/empty-state";

export default function PlansPage() {
  const token = useAuthStore((s) => s.accessToken);
  const [top1, setTop1] = useState("");

  const { data = [], refetch } = useQuery({
    queryKey: ["plans"],
    queryFn: () => api<Plan[]>("/api/v1/plans", {}, token || undefined),
    enabled: !!token,
  });

  async function createPlan(e: FormEvent) {
    e.preventDefault();
    if (!token) return;
    await api("/api/v1/plans", { method: "POST", body: JSON.stringify({ date: new Date().toISOString().slice(0, 10), reflection: "", items: [{ title: top1, status: "todo", estimate_minutes: 30, tags: "priority" }] }) }, token);
    setTop1("");
    refetch();
  }

  return (
    <>
      <h1 className="text-2xl font-bold">Plans</h1>
      <Card>
        <form className="flex gap-2" onSubmit={createPlan}>
          <Input placeholder="Top priority for today" value={top1} onChange={(e) => setTop1(e.target.value)} />
          <Button>Add</Button>
        </form>
      </Card>
      {data.length === 0 ? <EmptyState title="No plans yet" subtitle="Create your first daily plan." /> : (
        <div className="space-y-2">
          {data.map((p) => (
            <Card key={p.id}>
              <p className="font-semibold">{p.date}</p>
              <ul className="mt-2 list-disc pl-5 text-sm">
                {p.items.map((it) => <li key={it.id}>{it.title} ({it.status})</li>)}
              </ul>
            </Card>
          ))}
        </div>
      )}
    </>
  );
}
