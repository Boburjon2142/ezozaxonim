"use client";

import { FormEvent, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useAuthStore } from "@/store/auth";
import { TimeSession } from "@/lib/types";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function TimePage() {
  const token = useAuthStore((s) => s.accessToken);
  const [minutes, setMinutes] = useState(25);
  const [tags, setTags] = useState("focus");

  const { data = [], refetch } = useQuery({
    queryKey: ["sessions"],
    queryFn: () => api<TimeSession[]>("/api/v1/sessions", {}, token || undefined),
    enabled: !!token,
  });

  async function addManual(e: FormEvent) {
    e.preventDefault();
    if (!token) return;
    const end = new Date();
    const start = new Date(end.getTime() - minutes * 60000);
    await api("/api/v1/sessions", { method: "POST", body: JSON.stringify({ started_at: start.toISOString(), ended_at: end.toISOString(), tags }) }, token);
    refetch();
  }

  return (
    <>
      <h1 className="text-2xl font-bold">Time Sessions</h1>
      <Card>
        <form onSubmit={addManual} className="grid gap-2 md:grid-cols-3">
          <Input type="number" value={minutes} onChange={(e) => setMinutes(Number(e.target.value))} />
          <Input value={tags} onChange={(e) => setTags(e.target.value)} placeholder="tags" />
          <Button>Add Manual Session</Button>
        </form>
      </Card>
      <Card>
        <table className="w-full text-sm">
          <thead><tr><th className="text-left">Start</th><th>Duration</th><th>Tags</th></tr></thead>
          <tbody>
            {data.map((s) => (
              <tr key={s.id} className="border-t border-black/5">
                <td className="py-2">{new Date(s.started_at).toLocaleString()}</td>
                <td className="text-center">{s.duration_minutes}m</td>
                <td className="text-center">{s.tags}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </>
  );
}
