"use client";

import { FormEvent, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api } from "@/lib/api";
import { useAuthStore } from "@/store/auth";
import { CheckIn } from "@/lib/types";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function CheckinsPage() {
  const token = useAuthStore((s) => s.accessToken);
  const [note, setNote] = useState("");

  const { data = [], refetch } = useQuery({
    queryKey: ["checkins"],
    queryFn: () => api<CheckIn[]>("/api/v1/checkins", {}, token || undefined),
    enabled: !!token,
  });

  async function submit(e: FormEvent) {
    e.preventDefault();
    if (!token) return;
    await api("/api/v1/checkins", { method: "POST", body: JSON.stringify({ date: new Date().toISOString().slice(0, 10), energy: 3, stress: 3, mood: 3, sleep: 3, note }) }, token);
    setNote("");
    refetch();
  }

  const trend = data.slice(0, 14).reverse().map((d) => ({ date: d.date.slice(5), stress: d.stress, energy: d.energy }));

  return (
    <>
      <h1 className="text-2xl font-bold">Check-ins</h1>
      <Card>
        <form onSubmit={submit} className="flex gap-2">
          <Input placeholder="How are you feeling?" value={note} onChange={(e) => setNote(e.target.value)} />
          <Button>Quick Save</Button>
        </form>
      </Card>
      <Card className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={trend}>
            <XAxis dataKey="date" />
            <YAxis domain={[1, 5]} />
            <Tooltip />
            <Line dataKey="stress" stroke="#c15a24" />
            <Line dataKey="energy" stroke="#1c7a64" />
          </LineChart>
        </ResponsiveContainer>
      </Card>
    </>
  );
}
