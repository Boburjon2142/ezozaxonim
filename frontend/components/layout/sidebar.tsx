"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const links = [
  ["/today", "Today"],
  ["/plans", "Plans"],
  ["/time", "Time"],
  ["/checkins", "Check-ins"],
  ["/insights", "Insights"],
  ["/settings", "Settings"],
  ["/org", "Org"],
] as const;

export function Sidebar() {
  const path = usePathname();
  return (
    <aside className="surface h-fit w-full p-3 md:sticky md:top-4 md:w-56">
      <p className="px-2 pb-3 text-lg font-bold">LifePause</p>
      <nav className="space-y-1">
        {links.map(([href, label]) => (
          <Link
            key={href}
            href={href}
            className={cn(
              "block rounded-lg px-3 py-2 text-sm",
              path === href ? "bg-primary text-white" : "hover:bg-muted"
            )}
          >
            {label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
