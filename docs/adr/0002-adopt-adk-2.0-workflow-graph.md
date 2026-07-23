# ADR 0002 — Adopt ADK 2.x and add a Workflow-graph entrypoint

**Status:** Accepted · 2026-07-23

## Context

The project scaffolded on ADK 1.x (pinned `<2.0.0`, installed 1.36.2). ADK 2.0
went GA (Python 2.0.0, 2026-05-19; now 2.5.0) and introduces a graph-based
`Workflow` engine — nodes/edges, conditional routing, loops, and human-in-the-loop
interrupts. Two things prompted the change:

1. Our dependency was a major version behind the GA release.
2. Review feedback: the hierarchical crew read as a one-way waterfall with no
   visible agent feedback. LLM sub-agent transfer *is* bidirectional, but the
   feedback loop (flag → revise → re-check) was implicit in the Line Producer's
   reasoning rather than an explicit, inspectable structure.

## Decision

- **Bump to `google-adk >=2.0.0,<3.0.0`.** The existing hierarchical crew
  (`Agent`/`sub_agents`) runs unchanged on 2.5.0 — verified: imports, assembles,
  6→7 unit tests pass, mock MCP boots.
- **Keep the hierarchical crew** (`app/agent.py`) as the A2A/live-capable
  entrypoint. `Workflow` does not support `Runner.run_live`, and A2A serving is
  wired to the hierarchical app.
- **Add a second entrypoint** (`app/workflow.py`) expressing the same crew as an
  ADK 2.0 `Workflow` graph: `START → Continuity → gate` (routes on state flags)
  `→ Director review` (HITL interrupt) with a `revise → Continuity` routed cycle,
  else `→ Storyboard → Post-Production → finalize`.

## Consequences

**Positive**
- The feedback loop is now first-class and inspectable (a real routed cycle),
  directly answering the "waterfall" critique.
- Explicit HITL interrupt node instead of an implicit override tool.
- On the GA line; the 2.0 graph features are available going forward.

**Negative / cost**
- Two orchestration surfaces to keep coherent over the same role-agents.
- `Workflow` can't do live/bidi streaming — hence keeping the hierarchical app.
- Graph nodes must be `single_turn`; role-agents are reused as single-turn clones.

## Alternatives considered

- **Stay on 1.x.** Rejected: a major version behind GA, and no first-class graph
  feedback.
- **Replace the hierarchical crew entirely with the graph.** Rejected: loses A2A/
  live capability and the LLM-driven flexibility that suits open-ended requests.
- **Graph edges as 3-tuples** (per the skill cheatsheet). Rejected — the installed
  2.5 API rejects it; conditional routing uses a `{route: target}` dict, verified
  against the package.
