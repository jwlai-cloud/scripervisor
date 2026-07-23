# ADR 0001 — Front Desk has no planning authority

**Status:** Accepted · 2026-07-23

## Context

The crew needs a user-facing surface where a filmmaker types plain-English
requests. The obvious, cheapest design is a single agent that both talks to the
user *and* plans the work (breaks down shots, picks models, writes generation
prompts, delegates). That is also exactly what "a prompt box with a system
prompt" looks like — the thing the hackathon framing explicitly asks us to beat.

## Decision

Split the two responsibilities across two agents:

- **Front Desk** — user-facing, a *mover not a creator*. Collects the request,
  lightly validates, and transfers. No planner attached; its only real tool is
  transfer to the Line Producer. It never decides shot breakdown, order, model
  choice, or writes prompts.
- **Line Producer** — backend orchestrator, *not* user-facing. Holds the
  `PlanReActPlanner`, all delegation authority, and the human-in-the-loop gate.

The user never talks directly to the agent making creative/technical decisions.

## Consequences

**Positive**
- Concrete answer to "why is this more than a prompt box": the reasoning agent
  is structurally separated from the chat surface.
- Clean UX boundary — the Front Desk maps to the left request panel; the Line
  Producer's work becomes the Shot Board, not a chat transcript.
- Role-agents have one obvious parent to report to; delegation stays legible.

**Negative / cost**
- One extra transfer hop per request (Front Desk → Line Producer) — negligible
  latency, one more agent to maintain.
- Two instruction sets to keep coherent instead of one.

## Alternatives considered

- **Single planning-and-chat agent.** Simpler, one fewer hop. Rejected: it
  collapses the exact distinction the product is trying to demonstrate, and
  pushes the crew's reasoning into a chat log rather than the Shot Board.
- **Front Desk with a lightweight planner.** Rejected: any planning authority at
  the chat surface reintroduces the "prompt box" ambiguity we're avoiding.
