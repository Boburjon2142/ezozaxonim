"use client";

import { useQuery } from "@tanstack/react-query";
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api } from "@/lib/api";
import { useAuthStore } from "@/store/auth";
import { Card } from "@/components/ui/card";

type Insights = {
  energy_balance_score: number;
  weekly_work_vs_stress: { label: string; value: number }[];
  top_tags: { label: string; value: number }[];
  break_compliance: number;
  recommendations: string[];
};

export default function InsightsPage() {
  const token = useAuthStore((s) => s.accessToken);
  const { data } = useQuery({
    queryKey: ["insights"],
    queryFn: () => api<Insights>("/api/v1/insights", {}, token || undefined),
    enabled: !!token,
  });

  return (
    <>
      <h1 className="text-2xl font-bold">Insights</h1>
      <div className="grid gap-4 md:grid-cols-3">
        <Card><p className="text-sm">Energy Balance</p><p className="text-4xl font-bold">{data?.energy_balance_score ?? "-"}</p></Card>
        <Card><p className="text-sm">Break Compliance</p><p className="text-4xl font-bold">{data?.break_compliance ?? "-"}%</p></Card>
        <Card><p className="text-sm">Focus Signal</p><p className="text-4xl font-bold">{(data?.energy_balance_score ?? 0) > 70 ? "Stable" : "Needs Care"}</p></Card>
      </div>
      <Card className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data?.weekly_work_vs_stress ?? []}>
            <XAxis dataKey="label" hide />
            <YAxis />
            <Tooltip />
            <Bar dataKey="value" fill="#1c7a64" />
          </BarChart>
        </ResponsiveContainer>
      </Card>
      <Card>
        <p className="font-semibold">Action recommendations</p>
        <ul className="mt-2 list-disc pl-5 text-sm">
          {(data?.recommendations ?? []).map((r) => <li key={r}>{r}</li>)}
        </ul>
      </Card>
    </>
  );
}
