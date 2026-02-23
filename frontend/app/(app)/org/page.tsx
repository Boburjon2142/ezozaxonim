"use client";

import { useState } from "react";
import { useAuthStore } from "@/store/auth";
import { api } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

type OrgStats = {
  avg_work_hours: number;
  avg_break_compliance: number;
  avg_stress: number;
  burnout_risk_index: number;
  team_distribution: Record<string, number>;
};

export default function OrgPage() {
  const token = useAuthStore((s) => s.accessToken);
  const [orgId, setOrgId] = useState("");
  const [stats, setStats] = useState<OrgStats | null>(null);

  async function load() {
    if (!token || !orgId) return;
    const data = await api<OrgStats>(`/api/v1/org/${orgId}/dashboard`, {}, token);
    setStats(data);
  }

  return (
    <>
      <h1 className="text-2xl font-bold">Organization Dashboard</h1>
      <Card>
        <div className="flex gap-2">
          <Input placeholder="Organization ID" value={orgId} onChange={(e) => setOrgId(e.target.value)} />
          <Button onClick={load}>Load</Button>
        </div>
      </Card>
      {stats && (
        <div className="grid gap-4 md:grid-cols-4">
          <Card><p className="text-sm">Avg Work Hours</p><p className="text-3xl font-bold">{stats.avg_work_hours}</p></Card>
          <Card><p className="text-sm">Break Compliance</p><p className="text-3xl font-bold">{stats.avg_break_compliance}%</p></Card>
          <Card><p className="text-sm">Avg Stress</p><p className="text-3xl font-bold">{stats.avg_stress}</p></Card>
          <Card><p className="text-sm">Burnout Risk</p><p className="text-3xl font-bold">{stats.burnout_risk_index}</p></Card>
        </div>
      )}
      <Card>
        <p className="text-sm">Reports</p>
        <div className="mt-2 flex gap-2">
          <a className="rounded-lg bg-black px-3 py-2 text-sm text-white" href={`http://localhost:8000/api/v1/org/${orgId}/report.csv`} target="_blank">Download CSV</a>
          <a className="rounded-lg bg-black px-3 py-2 text-sm text-white" href={`http://localhost:8000/api/v1/org/${orgId}/report.pdf`} target="_blank">Download PDF</a>
        </div>
      </Card>
    </>
  );
}
