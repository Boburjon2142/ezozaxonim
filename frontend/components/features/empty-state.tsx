export function EmptyState({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <div className="surface p-8 text-center">
      <p className="text-lg font-semibold">{title}</p>
      <p className="mt-1 text-sm text-black/60">{subtitle}</p>
    </div>
  );
}
