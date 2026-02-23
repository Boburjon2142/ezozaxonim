"use client";

import { ReactNode } from "react";
import { Sidebar } from "@/components/layout/sidebar";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="mx-auto flex max-w-7xl flex-col gap-4 p-4 md:flex-row">
      <Sidebar />
      <main className="flex-1 space-y-4">{children}</main>
    </div>
  );
}
