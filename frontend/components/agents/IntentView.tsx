export function IntentView({
  intent,
  subTasks,
  agentsUsed
}: {
  intent: string;
  subTasks: string[];
  agentsUsed: string[];
}) {
  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-900/40 p-4">
      <div className="text-sm text-zinc-400">Orchestrator</div>

      <div className="mt-2">
        <div className="text-xs text-zinc-500">Intent</div>
        <div className="mt-1 inline-flex rounded-lg bg-zinc-800 px-3 py-1 text-sm">
          {intent}
        </div>
      </div>

      <div className="mt-4">
        <div className="text-xs text-zinc-500">Sub-tasks</div>
        <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-zinc-200">
          {subTasks?.length ? subTasks.map((t, i) => <li key={i}>{t}</li>) : <li>(none)</li>}
        </ul>
      </div>

      <div className="mt-4">
        <div className="text-xs text-zinc-500">Agents activated</div>
        <div className="mt-2 flex flex-wrap gap-2">
          {agentsUsed.map((a) => (
            <span key={a} className="rounded-lg bg-zinc-800 px-2 py-1 text-xs text-zinc-200">
              {a}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
