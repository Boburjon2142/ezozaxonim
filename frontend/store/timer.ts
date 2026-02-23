"use client";

import { create } from "zustand";

type TimerState = {
  running: boolean;
  startedAt: number | null;
  elapsedSec: number;
  mode: "focus" | "break";
  setMode: (mode: "focus" | "break") => void;
  start: () => void;
  stop: () => void;
  tick: () => void;
  reset: () => void;
};

export const useTimerStore = create<TimerState>((set, get) => ({
  running: false,
  startedAt: null,
  elapsedSec: 0,
  mode: "focus",
  setMode: (mode) => set({ mode }),
  start: () => set({ running: true, startedAt: Date.now() }),
  stop: () => set({ running: false }),
  tick: () => {
    const { running } = get();
    if (!running) return;
    set((s) => ({ elapsedSec: s.elapsedSec + 1 }));
  },
  reset: () => set({ elapsedSec: 0, startedAt: null, running: false }),
}));
