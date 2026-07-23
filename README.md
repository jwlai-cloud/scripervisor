# Scripervisor

**An open, extensible multi-agent film production crew on Google ADK, with a pluggable skills marketplace.**

Scripervisor (Script + Supervisor) is a submission for the [Agentic Cinema hackathon](https://agentic-cinema.devpost.com). A coordinator agent (**Line Producer**) delegates across a small set of role-agents — **Script/Continuity**, **Storyboard**, and a **Post-Production/Asset** agent wired to a partner MCP server — while every agent's capabilities are defined by loadable skill packages that any studio, freelancer, or partner can drop in without forking the system.

The product spine is a **Shot Board**: sequential visual shots that gain status (drafted → flagged → approved → assembled/rendered) as the crew works, with inline continuity/rights flags and a linear, append-only revision log. Terms are pinned in [CONTEXT.md](./CONTEXT.md).

> **Status:** crew scaffolded on **ADK 2.x** (A2A-ready) with a local mock MCP server and the Shot Board UI. The real partner MCP endpoint swaps in via one env var (`PARTNER_MCP_URL`) once the roster is announced (week of Jul 27).

## Two entrypoints

- **`app/agent.py`** — the hierarchical crew (LLM-driven delegation, A2A/live-capable). Front Desk → Line Producer → role-agents.
- **`app/workflow.py`** — the *same* work as an **ADK 2.0 `Workflow` graph**: orchestration is explicit edges, so the feedback loop is first-class — continuity-first, a director-review HITL interrupt, and a `revise → re-check` cycle before storyboarding/assembly. Not a one-way waterfall.

## Architecture (summary)

Built on Google's Agent Development Kit (ADK 2.x). The org chart:

```
Front Desk (root, router — no planning authority)
  └─ Line Producer (orchestrator, PlanReActPlanner)
       ├─ Script/Continuity   ── MCP: metadata_lookup
       ├─ Storyboard          (2-3 variant frames per shot)
       └─ Post-Production/Asset ── MCP: asset_search, rights_lookup
```

- **Front Desk** — thin user-facing router (a mover, not a creator); collects the plain-English request and hands off. No planner.
- **Line Producer** — backend orchestrator with `PlanReActPlanner`; owns requirement understanding, shot breakdown, model/tool selection, delegation, and the human-in-the-loop override gate (`require_confirmation`).
- **Script/Continuity** — cross-references new content against canon pulled from production metadata (MCP) and flags conflicts. **Storyboard** — generates 2-3 rough variants per shot (pick-then-polish). Rights & Clearance is a stretch goal.
- **Post-Production/Asset** — talks to a partner MCP server via ADK `McpToolset`; runs against the local mock stub (`mcp_server/mock_server.py`) until the real endpoint is announced, so the swap is a config change (`PARTNER_MCP_URL`), not a re-architecture.

Shared `session.state` (`shots`, `revision_log`, `activity`, `capability_gaps`) is the single source of truth the Shot Board UI renders from.

## Running locally

```bash
uv sync                                   # install deps
cp .env.example .env                      # set GOOGLE_CLOUD_PROJECT etc.
uv run --with pytest pytest tests/unit -q # network-free unit tests
uv run uvicorn app.fast_api_app:app --port 8000   # serve the crew (A2A card at /a2a/app/.well-known/agent-card.json)
```

Open `frontend/index.html` in a browser for the Shot Board (seeded with the demo scenario; wire to the backend by replacing the seed in `frontend/app.js`).

## Repository layout

```
app/                 ADK crew (agent.py assembles the org chart)
  sub_agents/        front_desk, line_producer, script_continuity, storyboard, post_production
  tools.py           shared session.state tools (shot board, revision log, HITL override)
  config.py          model + MCP swap-point (mock stdio ⇄ partner SSE)
mcp_server/          local mock MCP server (asset_search / metadata_lookup / rights_lookup)
frontend/            Shot Board UI (three-panel, no build step)
tests/               unit (no network) + integration (live A2A/Vertex)
```

## Governance

`master` is protected: all changes land via pull request (direct pushes, force-pushes, and branch deletion are blocked; open review conversations must be resolved before merge). This is intentional — the governed workflow is part of the project's own "Studio Head enforcing governance" story.

## Contributing

Work happens on `dev` / feature branches and merges into `master` via PR.

## License

[Apache License 2.0](./LICENSE).

---

_The detailed architecture / strategy brief (`agentic-cinema-plan.md`) is kept private and is intentionally excluded from this public repo._
