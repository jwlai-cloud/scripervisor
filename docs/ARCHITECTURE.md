# Scripervisor — Architecture

An open, extensible multi-agent film production **crew** on Google ADK. A
coordinator delegates across role-agents that break a filmmaker's plain-English
request into continuity-checked, pre-visualised **Shots** on a live **Shot Board**.
Terms used below are pinned in [`../CONTEXT.md`](../CONTEXT.md).

## Components

| Component | Where | Responsibility |
|---|---|---|
| **Front Desk** | `app/sub_agents/front_desk.py` | User-facing router. Collects the request, lightly validates, hands off. No planner, no creative authority. |
| **Line Producer** | `app/sub_agents/line_producer.py` | Orchestrator with `PlanReActPlanner`. Owns breakdown, delegation, tool/model choice, and the human-in-the-loop override gate. |
| **Script/Continuity** | `app/sub_agents/script_continuity.py` | Cross-references new content against **Canon** (via MCP `metadata_lookup`) and raises **Flags**. Reasoning only. |
| **Storyboard** | `app/sub_agents/storyboard.py` | Generates 2–3 rough **Variants** per Shot (pick-then-polish). |
| **Post-Production/Asset** | `app/sub_agents/post_production.py` | Retrieves existing footage (MCP `asset_search`), clears rights (`rights_lookup`), **Assembles** it. Retrieval, not generation. |
| **Shared tools** | `app/tools.py` | `session.state` mutators: shot board, revision log, capability gaps, and the `require_confirmation` override. |
| **MCP swap-point** | `app/config.py` | One function returns an `McpToolset` bound to the mock (stdio) or the partner (`PARTNER_MCP_URL`, SSE). |
| **Mock MCP server** | `mcp_server/mock_server.py` | FastMCP stub: `metadata_lookup` / `asset_search` / `rights_lookup`. Stands in for the partner endpoint (revealed week of Jul 27). |
| **A2A / HTTP server** | `app/fast_api_app.py` | Serves the crew over A2A (agent card + JSON-RPC) via the ADK `adk_a2a` template. |
| **Shot Board UI** | `frontend/` | Three-panel console rendering from the `session.state` shape. |

## ADK topology (reasoning structure)

Hierarchical LLM delegation: each parent transfers control to a child. The Line
Producer is the only agent with a planner; the Front Desk is a deliberately thin
router (see [ADR 0001](./adr/0001-front-desk-no-planning-authority.md)).

```mermaid
graph TD
    U([Filmmaker]) -->|plain-English request| FD["🎬 Front Desk<br/><i>router · no planner</i>"]
    FD -->|transfer| LP["🎯 Line Producer<br/><i>orchestrator · PlanReActPlanner</i>"]

    LP -->|delegate| SC["📋 Script/Continuity"]
    LP -->|delegate| SB["🎨 Storyboard"]
    LP -->|delegate| PP["🎞️ Post-Production/Asset"]

    LP -.->|require_confirmation| HITL{{"Human-in-the-loop<br/>override gate"}}

    SC -->|metadata_lookup| MCP[["MCP swap-point<br/>app/config.py"]]
    PP -->|asset_search · rights_lookup| MCP
    MCP -->|stdio now| MOCK[("Mock MCP server")]
    MCP -.->|SSE later · PARTNER_MCP_URL| PARTNER[("Partner MCP server")]

    SC & SB & PP -->|read/write| STATE[("session.state<br/>shots · revision_log<br/>activity · capability_gaps")]
    STATE --> UI["🖥️ Shot Board UI"]

    classDef router fill:#1f2937,stroke:#e3b341,color:#fff;
    classDef orch fill:#3b2f0b,stroke:#e3b341,color:#fff;
    classDef role fill:#15202b,stroke:#58a6ff,color:#fff;
    classDef ext fill:#12261a,stroke:#3fb950,color:#fff;
    class FD router; class LP orch; class SC,SB,PP role; class MOCK,PARTNER,MCP ext;
```

## Orchestration shape

- **Hierarchical, LLM-driven** (not a fixed `SequentialAgent` pipeline): the Line
  Producer reasons about *which* role-agent to transfer to and *when*, because a
  request may or may not need a continuity check, storyboard, or asset pass.
- **Continuity-first rule**: the Line Producer's instruction forces a
  Script/Continuity pass before anything is drawn or assembled.
- **Human-in-the-loop**: overriding a continuity Flag is a `require_confirmation`
  tool — the director's reason is captured as the Revision rationale.

## Data flow — one representative request

Request: *"Add a night scene where the detective loses her badge."*

1. **Filmmaker → Front Desk**: submits the request in plain English.
2. **Front Desk → Line Producer**: confirms understanding, transfers. Makes no plan.
3. **Line Producer**: breaks it into Shots; transfers to Script/Continuity first.
4. **Script/Continuity → MCP**: `metadata_lookup("badge")` → canon says *badge already lost in Scene 4*.
5. **Script/Continuity**: raises a **Flag** on the shot (conflict: badge can't be lost twice).
6. **Line Producer → Filmmaker**: surfaces the conflict; on "approve anyway" calls the `require_confirmation` override, capturing the reason → **Revision** log.
7. **Line Producer → Storyboard**: generates 2–3 **Variants** for the corrected shot.
8. **Line Producer → Post-Production**: `asset_search` finds a night city plate, `rights_lookup` clears it → **Assembled**.
9. **Shot Board UI**: reflects each status change live (drafted → flagged → approved → assembled), plus skill badges and the revision log.

```mermaid
sequenceDiagram
    actor F as Filmmaker
    participant FD as Front Desk
    participant LP as Line Producer
    participant SC as Script/Continuity
    participant M as MCP (mock→partner)
    participant SB as Storyboard
    participant PP as Post-Production
    participant S as session.state / Shot Board

    F->>FD: "night scene, detective loses badge"
    FD->>LP: transfer (no plan)
    LP->>SC: break down + continuity-check first
    SC->>M: metadata_lookup("badge")
    M-->>SC: lost in Scene 4 (canon)
    SC->>S: FLAG shot (conflict)
    S-->>F: inline flag banner
    F->>LP: "approve anyway" + reason
    LP->>S: override (require_confirmation) → Revision logged
    LP->>SB: generate variants
    SB->>S: 2–3 variants (drafted)
    LP->>PP: find + clear asset
    PP->>M: asset_search / rights_lookup
    M-->>PP: PLATE-014 (cleared)
    PP->>S: assembled
```

## Status state machine

A Shot's `status` is a state machine, not a free label. A **Flag** can interrupt
from any state; a Shot never regresses from Approved/Assembled/Rendered.

```
drafted ──▶ flagged ──(override, reason)──▶ approved ──▶ assembled  (existing asset attached)
   │                                            │
   └────────────── clean ───────────────────────┘        └──▶ rendered (original polished frame)
```

## External dependencies

- **Google ADK** (`google-adk >= 1.27`) — `Agent`, `PlanReActPlanner`, `McpToolset`, `require_confirmation`, `Runner`, `App`.
- **Gemini via Vertex AI** — reasoning/routing model (`gemini-flash-latest` default); Imagen for real storyboard frames (mock generator today).
- **A2A** (`a2a-sdk`) — the crew is exposed as an A2A agent (card + JSON-RPC) so other agentic tools can call it.
- **MCP** (`mcp`) — partner asset/metadata/rights server; local mock stub until the roster reveal.

## Extensibility — the differentiator

- **Skills**: loadable capability bundles that extend any agent at runtime without forking (on-disk format planned per the skill-loader design).
- **Capability gaps**: when an agent hits something it can't do, `report_capability_gap` files structured telemetry naming the Skill that would close it — gap → skill request → loadable by every crew. Not a forum.
