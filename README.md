# Scripervisor

**An open, extensible multi-agent film production crew on Google ADK, with a pluggable skills marketplace.**

Scripervisor (Script + Supervisor) is a submission for the [Agentic Cinema hackathon](https://agentic-cinema.devpost.com). A coordinator agent (**Line Producer**) delegates across a small set of role-agents — **Script/Continuity**, **Storyboard**, and a **Post-Production/Asset** agent wired to a partner MCP server — while every agent's capabilities are defined by loadable skill packages that any studio, freelancer, or partner can drop in without forking the system.

The product spine is a **Shot Board**: sequential visual shots that gain status (drafted → flagged → approved → rendered) as the crew works, with inline continuity/rights flags and a linear, append-only revision log.

> **Status:** Phase 0 — repo governance set up. Agent scaffolding lands in a later PR once the hackathon partner roster is announced (week of Jul 27) and the remaining architecture decisions are confirmed.

## Architecture (summary)

Built on Google's Agent Development Kit (ADK):

- **Front Desk** — thin user-facing router (a mover, not a creator); collects the plain-English request and hands off. No planning authority.
- **Line Producer** — backend orchestrator; owns requirement understanding, shot breakdown, model/tool selection, and delegation across sub-agents.
- **Script/Continuity** & **Storyboard** — launch sub-agents. Rights & Clearance is a stretch goal.
- **Post-Production/Asset** — talks to a partner MCP server via ADK `McpToolset`; runs against a local mock MCP stub until the real partner endpoint is announced, so the swap is a config change, not a re-architecture.

## Governance

`master` is protected: all changes land via pull request (direct pushes, force-pushes, and branch deletion are blocked; open review conversations must be resolved before merge). This is intentional — the governed workflow is part of the project's own "Studio Head enforcing governance" story.

## Contributing

Work happens on `dev` / feature branches and merges into `master` via PR.

## License

[Apache License 2.0](./LICENSE).

---

_The detailed architecture / strategy brief (`agentic-cinema-plan.md`) is kept private and is intentionally excluded from this public repo._
