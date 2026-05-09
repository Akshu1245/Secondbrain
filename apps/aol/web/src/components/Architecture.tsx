"use client";

/**
 * Compact architecture diagram for the Second Brain landing area.
 * Reads a 3-second story: the user's apps and the OEM AI assistant
 * never talk directly — every call passes through Second Brain, which decides
 * what to surface, where to compute, and what to remember.
 */
export function Architecture() {
  return (
    <div id="how-it-fits-in" className="rounded-2xl border border-ink-800 bg-ink-950/60 p-5">
      <div className="mb-3 flex flex-wrap items-baseline justify-between gap-3">
        <h2 className="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-400/80">
          Where Second Brain sits
        </h2>
        <span className="text-xs text-gray-500">
          The user&rsquo;s apps don&rsquo;t talk to the AI assistant directly. Second Brain is in between, and decides what happens.
        </span>
      </div>
      <svg
        viewBox="0 0 880 240"
        role="img"
        aria-label="Second Brain middleware sits between the user's apps and the OEM AI assistant"
        className="h-auto w-full max-w-full"
      >
        <defs>
          <linearGradient id="aol-band" x1="0" x2="1" y1="0" y2="0">
            <stop offset="0" stopColor="#34d399" stopOpacity="0.18" />
            <stop offset="1" stopColor="#34d399" stopOpacity="0.06" />
          </linearGradient>
          <marker
            id="arrow"
            viewBox="0 0 10 10"
            refX="9"
            refY="5"
            markerWidth="6"
            markerHeight="6"
            orient="auto-start-reverse"
          >
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#34d399" />
          </marker>
        </defs>

        {/* ──────────────── Left: User device ──────────────── */}
        <g>
          <rect
            x="20"
            y="50"
            width="150"
            height="140"
            rx="14"
            fill="#0f1419"
            stroke="#26303a"
          />
          <text x="95" y="38" textAnchor="middle" fill="#9ca3af" fontSize="11" fontWeight="600" letterSpacing="2">
            USER DEVICE
          </text>
          <text x="95" y="78" textAnchor="middle" fill="#e5e7eb" fontSize="13" fontWeight="600">
            Apps + OS
          </text>
          <text x="95" y="100" textAnchor="middle" fill="#9ca3af" fontSize="11">
            messaging · camera
          </text>
          <text x="95" y="116" textAnchor="middle" fill="#9ca3af" fontSize="11">
            calls · notes · keyboard
          </text>
          <text x="95" y="148" textAnchor="middle" fill="#6b7280" fontSize="10">
            user preferences
          </text>
          <text x="95" y="164" textAnchor="middle" fill="#6b7280" fontSize="10">
            battery · data · privacy
          </text>
        </g>

        {/* arrow user → Second Brain */}
        <line
          x1="170"
          y1="120"
          x2="240"
          y2="120"
          stroke="#34d399"
          strokeWidth="2"
          markerEnd="url(#arrow)"
        />

        {/* ──────────────── Middle: Second Brain middleware ──────────────── */}
        <g>
          <rect
            x="240"
            y="20"
            width="400"
            height="200"
            rx="18"
            fill="url(#aol-band)"
            stroke="#34d399"
            strokeOpacity="0.5"
          />
          <text x="440" y="42" textAnchor="middle" fill="#34d399" fontSize="11" fontWeight="700" letterSpacing="3">
            Second Brain — THE LAYER WE&apos;RE PITCHING
          </text>
          <text x="440" y="62" textAnchor="middle" fill="#e5e7eb" fontSize="13">
            ~131 lines of Kotlin · drops in once · runs in front of every AI call
          </text>

          {/* 6 module pills, 3x2 grid */}
          {[
            { x: 260, y: 88,  k: "1", label: "Hide unused" },
            { x: 380, y: 88,  k: "2", label: "Right-time" },
            { x: 500, y: 88,  k: "3", label: "Phone vs cloud" },
            { x: 260, y: 144, k: "4", label: "Log every call" },
            { x: 380, y: 144, k: "5", label: "Listen to user" },
            { x: 500, y: 144, k: "6", label: "Remember" },
          ].map((m) => (
            <g key={m.k}>
              <rect
                x={m.x}
                y={m.y}
                width="120"
                height="42"
                rx="10"
                fill="#0d1f1a"
                stroke="#34d39966"
              />
              <text x={m.x + 14} y={m.y + 18} fill="#34d399" fontSize="10" fontWeight="700">
                {m.k}
              </text>
              <text x={m.x + 60} y={m.y + 26} textAnchor="middle" fill="#e5e7eb" fontSize="11" fontWeight="600">
                {m.label}
              </text>
            </g>
          ))}

          <text x="440" y="208" textAnchor="middle" fill="#9ca3af" fontSize="10">
            decides: what surfaces · where compute lands · what to remember
          </text>
        </g>

        {/* arrow Second Brain → OEM */}
        <line
          x1="640"
          y1="100"
          x2="710"
          y2="100"
          stroke="#34d399"
          strokeWidth="2"
          markerEnd="url(#arrow)"
        />
        {/* arrow Second Brain → Cloud */}
        <line
          x1="640"
          y1="160"
          x2="710"
          y2="160"
          stroke="#60a5fa"
          strokeWidth="2"
          markerEnd="url(#arrow)"
        />

        {/* ──────────────── Right: OEM AI + Cloud ──────────────── */}
        <g>
          <rect
            x="710"
            y="50"
            width="150"
            height="60"
            rx="12"
            fill="#0f1419"
            stroke="#26303a"
          />
          <text x="785" y="76" textAnchor="middle" fill="#e5e7eb" fontSize="13" fontWeight="600">
            OEM AI assistant
          </text>
          <text x="785" y="94" textAnchor="middle" fill="#9ca3af" fontSize="10">
            Moto AI · Galaxy AI · Bixby
          </text>

          <rect
            x="710"
            y="130"
            width="150"
            height="60"
            rx="12"
            fill="#0f1419"
            stroke="#26303a"
          />
          <text x="785" y="156" textAnchor="middle" fill="#e5e7eb" fontSize="13" fontWeight="600">
            Cloud LLM
          </text>
          <text x="785" y="174" textAnchor="middle" fill="#60a5fa" fontSize="10">
            heavy / fresh-knowledge only
          </text>
        </g>
      </svg>
    </div>
  );
}
