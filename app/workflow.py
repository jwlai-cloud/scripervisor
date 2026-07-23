# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""The Line Producer's plan as an ADK 2.0 graph.

The hierarchical crew in `app/agent.py` uses LLM-driven delegation (Front Desk →
Line Producer → role-agents). This module expresses the *same* work as an ADK
2.0 `Workflow` graph, where the orchestration is explicit edges instead of an
LLM's transfer decisions — which lets us make the feedback loop first-class:

    START → Continuity ─▶ gate ─(clean)──────────────▶ Storyboard → Post-Prod → done
                            │                              ▲
                            └─(flagged)─▶ Director review ──┤ (approve)
                                              │
                                              └─(revise)─▶ back to Continuity   ← re-check loop

The revise edge is a real cycle: a flagged shot goes back through Continuity for
a fresh check after the director asks for a fix — not a one-way waterfall.

# ponytail: reuses the three leaf role-agents from app/sub_agents as graph nodes
# (they have no sub_agents, so no transfer behaviour to fight). Front Desk /
# Line Producer routing becomes the graph itself.
"""

from typing import Any

from google.adk.agents.context import Context
from google.adk.apps import App
from google.adk.events.event import Event
from google.adk.events.request_input import RequestInput
from google.adk.workflow import START, Workflow, node
from google.genai import types

from app.sub_agents.post_production import post_production
from app.sub_agents.script_continuity import script_continuity
from app.sub_agents.storyboard import storyboard

# Graph nodes must be single-turn: they consume a predecessor's output directly
# rather than replaying chat history. Clone the chat-mode role-agents as
# single-turn nodes; the originals stay chat-mode for the hierarchical crew.
_continuity = script_continuity.model_copy(update={"mode": "single_turn"})
_storyboard = storyboard.model_copy(update={"mode": "single_turn"})
_postprod = post_production.model_copy(update={"mode": "single_turn"})


@node(name="continuity_gate")
def continuity_gate(ctx: Context, node_input: Any) -> Event:
    """Route on whether Continuity left any flag in session state.

    Continuity communicates via state (its `flag_shot` tool writes onto the
    shot), so the gate routes on that rather than parsing free-text output —
    which is why Continuity can keep its MCP/flag tools (output_schema would
    disable them).
    """
    shots = ctx.state.get("shots", [])
    flagged = any(shot.get("flags") for shot in shots)
    return Event(output=node_input, route="flagged" if flagged else "clean")


@node(name="director_review", rerun_on_resume=True)
async def director_review(ctx: Context, node_input: Any):
    """Human-in-the-loop: pause on a flagged shot; route approve vs revise.

    Uses a per-round interrupt id so re-entering the loop asks a fresh question
    instead of restarting the same interrupt forever.
    """
    loop = ctx.state.get("review_round", 0)
    key = f"director_decision_{loop}"
    if key not in (ctx.resume_inputs or {}):
        yield RequestInput(
            interrupt_id=key,
            message=(
                "Continuity conflict on a shot. Reply 'approve: <reason>' to "
                "override (reason is logged as the revision rationale), or "
                "'revise' to send it back for a fix."
            ),
        )
        return
    decision = str(ctx.resume_inputs[key])
    if decision.strip().lower().startswith("approve"):
        yield Event(output=decision, route="approve", state={"override_reason": decision})
    else:
        yield Event(output=decision, route="revise", state={"review_round": loop + 1})


@node(name="finalize")
def finalize(ctx: Context, node_input: Any):
    """Emit the assembled shot list as a user-facing content event."""
    shots = ctx.state.get("shots", [])
    summary = f"Shot list ready — {len(shots)} shot(s) processed."
    yield Event(content=types.Content(role="model", parts=[types.Part.from_text(text=summary)]))
    yield Event(output=summary)


# The graph. START feeds the first real work (Continuity); Front Desk's "just
# hand off" role collapses into the entry edge.
scripervisor_graph = Workflow(
    name="scripervisor_graph",
    description=(
        "The Line Producer's plan as an ADK 2.0 graph: continuity-first, with a "
        "director-review HITL interrupt and a revise→re-check feedback loop "
        "before storyboarding and asset assembly."
    ),
    edges=[
        (START, _continuity),
        (_continuity, continuity_gate),
        # Conditional routing uses a {route: target} dict (ADK 2.5 edge form).
        (continuity_gate, {"flagged": director_review, "clean": _storyboard}),
        (director_review, {"revise": _continuity, "approve": _storyboard}),  # revise = feedback loop
        (_storyboard, _postprod),
        (_postprod, finalize),
    ],
)

root_agent = scripervisor_graph
workflow_app = App(name="scripervisor_graph", root_agent=scripervisor_graph)
