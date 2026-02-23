import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function LandingPage() {
  return (
    <main className="mx-auto max-w-6xl p-6 md:p-12">
      <section className="surface grid gap-6 overflow-hidden p-8 md:grid-cols-2">
        <div className="space-y-4">
          <p className="inline-block rounded-full bg-accent/10 px-3 py-1 text-xs font-semibold text-accent">LifePause</p>
          <h1 className="text-4xl font-bold leading-tight">Sustainable productivity, not burnout.</h1>
          <p className="text-black/70">Track work time, energy, breaks, and plans in one rhythm system that nudges action daily.</p>
          <div className="flex gap-3">
            <Link href="/signup"><Button>Start Free</Button></Link>
            <Link href="/login"><Button className="bg-black">Sign In</Button></Link>
          </div>
        </div>
        <div className="rounded-2xl bg-gradient-to-br from-primary/20 via-accent/20 to-transparent p-6">
          <p className="text-sm font-semibold">Product Pillars</p>
          <ul className="mt-3 space-y-2 text-sm">
            <li>Energy identification score</li>
            <li>Daily 60-second check-ins</li>
            <li>Smart break alerts + adaptive cycles</li>
            <li>Healthy rhythm trends over weeks</li>
            <li>Action-oriented recommendations</li>
          </ul>
        </div>
      </section>
    </main>
  );
}
