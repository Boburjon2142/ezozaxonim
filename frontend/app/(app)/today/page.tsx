"use client";

import { useEffect, useState } from "react";
import { useTimerStore } from "@/store/timer";
import { useAuthStore } from "@/store/auth";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";

export default function TodayPage() {
  const { elapsedSec, running, start, stop, tick, reset } = useTimerStore();
  const token = useAuthStore((s) => s.accessToken);
  const [energy, setEnergy] = useState(3);
  const [stress, setStress] = useState(3);

  useEffect(() => {
    const id = setInterval(() => tick(), 1000);
    return () => clearInterval(id);
  }, [tick]);

  const mins = Math.floor(elapsedSec / 60).toString().padStart(2, "0");
  const secs = (elapsedSec % 60).toString().padStart(2, "0");

  async function saveSession() {
    if (!token || elapsedSec < 60) return;
    const end = new Date();
    const startTime = new Date(end.getTime() - elapsedSec * 1000);
    await api("/api/v1/sessions", { method: "POST", body: JSON.stringify({ started_at: startTime.toISOString(), ended_at: end.toISOString(), tags: "focus" }) }, token);
    toast.success("Session saved");
    reset();
  }

  async function quickCheckin() {
    if (!token) return;
    await api("/api/v1/checkins", { method: "POST", body: JSON.stringify({ date: new Date().toISOString().slice(0, 10), energy, stress, mood: 3, sleep: 3, note: "Quick check-in" }) }, token);
    toast.success("Check-in saved");
  }

  async function sendBreak() {
    if (!token) return;
    await api("/api/v1/notifications/break", { method: "POST" }, token);
    toast.message("Break alert sent", { description: "Web push stub + in-app flow wired." });
  }

  return (
    <>
      <h1 className="text-2xl font-bold">Today</h1>
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <p className="text-sm text-black/60">Focus Timer</p>
          <p className="mt-2 text-5xl font-bold">{mins}:{secs}</p>
          <div className="mt-4 flex gap-2">
            <Button onClick={running ? stop : start}>{running ? "Pause" : "Start"}</Button>
            <Button className="bg-black" onClick={saveSession}>Save Session</Button>
            <Button className="bg-accent" onClick={sendBreak}>Break Alert</Button>
          </div>
        </Card>
        <Card>
          <p className="text-sm text-black/60">60-second check-in</p>
          <div className="mt-3 grid gap-2">
            <label className="text-sm">Energy (1-5)<Input type="number" min={1} max={5} value={energy} onChange={(e) => setEnergy(Number(e.target.value))} /></label>
            <label className="text-sm">Stress (1-5)<Input type="number" min={1} max={5} value={stress} onChange={(e) => setStress(Number(e.target.value))} /></label>
            <Button onClick={quickCheckin}>Save Check-in</Button>
          </div>
        </Card>
      </div>
    </>
  );
}
