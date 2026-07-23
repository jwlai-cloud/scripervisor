# Scripervisor

An open, extensible multi-agent film **crew** that turns a filmmaker's plain-English
request into a **Shot Board** of pre-visualised, continuity-checked shots. This
glossary is the crew's ubiquitous language — use these words, avoid the listed
alternatives.

## The Crew

**Crew**:
The full set of agents working a filmmaker's request together.
_Avoid_: team, swarm, pipeline

**Front Desk**:
The single user-facing agent. Takes the request, lightly validates it, and hands
off. A mover, not a creator — it has no planning authority.
_Avoid_: receptionist, chatbot, assistant

**Line Producer**:
The orchestrator. Owns requirement understanding, shot breakdown, delegation,
tool/model choice, and human-in-the-loop decisions. The only agent with a planner.
_Avoid_: Director, Producer, coordinator, manager, supervisor

**Role-agent**:
An agent that reports to the Line Producer and does one job: **Script/Continuity**,
**Storyboard**, or **Post-Production/Asset**. The Front Desk and Line Producer are
NOT role-agents (they route and orchestrate).
_Avoid_: worker, sub-agent (in prose), specialist

**Script/Continuity**:
The role-agent that cross-references new content against **Canon** and raises a
**Flag** on conflicts. Reasoning only — it generates no media.
_Avoid_: scripty, checker, validator

**Storyboard**:
The role-agent that produces **Variants** for a **Shot** and, once one is picked,
a polished **Frame**.
_Avoid_: artist, illustrator, image agent

**Post-Production/Asset**:
The role-agent that retrieves existing footage from the partner asset library,
clears its rights, and **Assembles** it into a Shot. Retrieval, not generation.
_Avoid_: editor, VFX, render agent

## The Board

**Shot Board**:
The primary surface: the live grid of **Shots**. Doubles as the session's
continuity-bible artifact by the end.
_Avoid_: canvas, timeline, storyboard (that's an agent), kanban

**Shot**:
One card on the Shot Board and the atomic unit of work. A Shot belongs to a
**Scene**. Continuity, storyboarding, and assembly all operate per-Shot.
_Avoid_: card, panel, frame (a Frame is the image, not the Shot)

**Scene**:
A narrative grouping of Shots (e.g. "the alley at night"). A label/parent for
Shots — never itself a board card.
_Avoid_: beat, sequence, clip; do NOT use Scene as the board unit

**Status**:
A Shot's position in its lifecycle. A state machine, not free labels — a Flag can
interrupt from any state, and a Shot must never regress from Approved/Assembled/
Rendered back to Drafted. States:
- **Drafted** — broken out and/or has rough Variants; not yet accepted.
- **Flagged** — a Continuity/rights conflict is open on it. Interrupts any state.
- **Approved** — the human accepted it (clean, or via **Override**).
- **Assembled** — a cleared existing asset has been attached (Post-Production path).
- **Rendered** — a polished original **Frame** has been produced (Storyboard/Imagen path).
_Avoid_: state, phase; "done" (say Assembled or Rendered — they mean different paths)

**Variant**:
One of the 2–3 rough, deliberately disposable compositions Storyboard offers per
Shot so the human can pick. Cheap and fast by design.
_Avoid_: draft, option, thumbnail, candidate

**Frame**:
The rendered image for the picked Variant (polished pass). One Frame per Shot.
_Avoid_: image, render, picture, still

## Continuity & Revision

**Canon**:
The established, authoritative facts of the production (props, wardrobe, story-day,
locations) — the "story bible" Script/Continuity checks against, retrieved via MCP.
_Avoid_: metadata, ground truth, facts, lore

**Flag**:
A specific, cited continuity or rights conflict raised on a Shot (e.g. "badge
already lost in Scene 4"). Surfaces as an inline banner, not a buried log line.
_Avoid_: error, bug, issue, warning

**Override**:
A deliberate human decision to Approve a Flagged Shot anyway. Requires explicit
confirmation; the stated reason becomes the Revision rationale.
_Avoid_: force, dismiss, ignore, bypass

**Revision**:
One entry in the linear, append-only revision log: what changed, why, and a
WGA-style colour label (Rev. White → Blue → Pink…). Never edited or reordered.
_Avoid_: version, commit, changelog, diff (no branches/merges exist)

## Skills & Gaps

**Skill** (a.k.a. **Skill package**):
A loadable capability bundle (manifest + scripts) that extends any agent at
runtime without forking the system. The product's core differentiator.
_Avoid_: plugin, extension, module, add-on, tool

**Skill badge**:
A marker on a Shot showing a Skill touched it (e.g. "day-for-night grading applied").
_Avoid_: tag, label, chip

**Capability gap**:
A structured report an agent files when it hits something it can't do, naming the
Skill that would close it. Turns pain-points into telemetry, not forum posts.
_Avoid_: bug, feedback, ticket, request, TODO
