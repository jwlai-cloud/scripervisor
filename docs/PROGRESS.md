# Scripervisor — Progress

_Snapshot as of 2026-07-23. Paused; resuming next week._

## Done

### Phase 0 — Governance (PR #1, merged)
- Public repo, Apache-2.0. `master` protected: PR required, **0 human approvals**
  (bot reviewers only), `enforce_admins`, no force-push/delete, conversation
  resolution required before merge.
- Branch model: `dev`/feature branches → PR → `master`.
- Repo hygiene: `.gitignore` (keeps the private strategy brief off the repo),
  `README.md`, `claude.md` build primer.

### Phase 1 — Crew scaffold (PR #2, merged)
- Google ADK crew, A2A-ready (scaffolded from the `adk_a2a` template):
  Front Desk (router) → Line Producer (`PlanReActPlanner`) →
  Script/Continuity + Storyboard + Post-Production/Asset.
- **MCP swap-point** (`app/config.py`): local mock over stdio now, partner SSE
  via `PARTNER_MCP_URL` later — one env var, no agent code changes.
- **Mock MCP server** (`mcp_server/`): `metadata_lookup` / `asset_search` /
  `rights_lookup`, canned around the demo (badge lost in Scene 4).
- **HITL**: `override_continuity_flag` = `require_confirmation`; reason →
  revision-log rationale.
- **Skill-economy hook**: `report_capability_gap` structured telemetry.
- **Shot Board UI** (`frontend/`): three-panel, no build step, inline flag banner.
- Verified: `ruff` clean, 6 unit tests pass, crew assembles, mock MCP boots.

### Domain model
- `CONTEXT.md` glossary (opinionated, with `_Avoid_` lists).
- Resolved 3 ambiguities and aligned code: **Shot ∈ Scene**;
  **`assembled` (retrieval) vs `rendered` (generation)** terminal split;
  **status is a state machine** (no regression from approved/assembled/rendered).
- [ADR 0001](./adr/0001-front-desk-no-planning-authority.md).

### ADK 2.0 + Workflow graph (PR #4, merged)
- Bumped to **ADK 2.x** (running 2.5.0); the hierarchical crew runs unchanged.
- Added a second entrypoint `app/workflow.py`: the crew as an ADK 2.0 `Workflow`
  graph with conditional routing, a director-review **HITL interrupt**, and a
  **revise → re-check feedback loop** (a real routed cycle) — the answer to the
  "waterfall / no feedback" critique.
- [ADR 0002](./adr/0002-adopt-adk-2.0-workflow-graph.md). Verified: 7 unit tests
  pass, `ruff` clean, both entrypoints construct, mock MCP boots on 2.5.

## Deferred (by plan)
- Real partner MCP endpoint — announced week of Jul 27; swaps in via `PARTNER_MCP_URL`.
- Rights & Clearance agent — stretch (Post-Production does `rights_lookup` for now).
- Imagen wiring for real storyboard frames — mock variant generator today.
- Live UI ↔ backend wiring — UI is seeded; stub documented in `frontend/app.js`.
- Scene *grouping* on the board (Shots roll up under a Scene parent) — model-faithful, not yet built.
- Skill-loader on-disk format + runtime loader.
- A2A discovery/composition demo with an external agent.

## Known risks
- **PRs #2, #3, #4 merged with no substantive bot review** (CodeRabbit + Sourcery
  rate-limited). A proper code-review pass over the merged crew is outstanding.
- The graph's **live end-to-end run** (HITL resume loop) is unverified — needs
  Vertex creds; only construction + ADK graph-validation is exercised.
- Video-gen latency is a live-demo risk — storyboard stays still-image by default.

## Next (next week)
1. Code-review pass over the merged crew (correctness + ADK idiom), once bot limits reset.
2. Live-run the Workflow graph end to end (HITL resume) against Vertex.
3. Wire the partner MCP once announced; keep mock as demo fallback.
4. Wire the Shot Board to the live backend (`session.state` → UI).
5. First skill package + runtime loader (the differentiator).
