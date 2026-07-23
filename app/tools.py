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

"""Shared crew tools.

These operate on `session.state`, which is the single source of truth the Shot
Board UI renders from:

  state["shots"]         -> list of shot cards (the board)
  state["revision_log"]  -> linear, append-only log with a rationale per entry
  state["activity"]      -> lightweight audit trail (who did what, when)
  state["capability_gaps"] -> structured "I couldn't do X" reports from agents
"""

from typing import Any

from google.adk.tools import FunctionTool, LongRunningFunctionTool, ToolContext

# WGA-style revision colour sequence — real productions label revised pages this
# way so anyone on set sees at a glance that something changed.
REVISION_COLORS = [
    "White",
    "Blue",
    "Pink",
    "Yellow",
    "Green",
    "Goldenrod",
    "Buff",
    "Salmon",
    "Cherry",
]


def _activity(tool_context: ToolContext, agent: str, message: str) -> None:
    """Append one entry to the audit trail. `seq` is a monotonic counter so the
    UI can order events without a wall clock (unavailable to agents at runtime).
    """
    log = tool_context.state.get("activity", [])
    log.append({"seq": len(log) + 1, "agent": agent, "message": message})
    tool_context.state["activity"] = log


def upsert_shot(
    shot_id: str,
    scene: str,
    status: str,
    agent: str,
    tool_context: ToolContext,
    note: str = "",
) -> dict[str, Any]:
    """Create or update a shot card on the Shot Board.

    Args:
        shot_id: Stable id for the shot, e.g. "S1" or "scene-7-a".
        scene: One-line description of the scene/shot.
        status: One of drafted | flagged | approved | rendered.
        agent: The agent making this change (shows as "last touched by").
        note: Optional short note surfaced on the card.
    """
    shots = tool_context.state.get("shots", [])
    for shot in shots:
        if shot["shot_id"] == shot_id:
            shot.update(scene=scene, status=status, last_touched_by=agent, note=note)
            break
    else:
        shots.append(
            {
                "shot_id": shot_id,
                "scene": scene,
                "status": status,
                "last_touched_by": agent,
                "note": note,
                "variants": [],
                "flags": [],
                "skill_badges": [],
            }
        )
    tool_context.state["shots"] = shots
    _activity(tool_context, agent, f"{status} shot {shot_id}: {scene}")
    return {"status": "ok", "shot_id": shot_id, "shot_status": status}


def flag_shot(
    shot_id: str, conflict: str, agent: str, tool_context: ToolContext
) -> dict[str, Any]:
    """Attach a continuity/rights conflict banner to a shot and mark it flagged.

    Args:
        shot_id: The shot the conflict is on.
        conflict: Human-readable conflict, e.g. "badge already lost in Scene 4".
        agent: The flagging agent.
    """
    shots = tool_context.state.get("shots", [])
    for shot in shots:
        if shot["shot_id"] == shot_id:
            shot.setdefault("flags", []).append(conflict)
            shot["status"] = "flagged"
            break
    tool_context.state["shots"] = shots
    _activity(tool_context, agent, f"FLAG on {shot_id}: {conflict}")
    return {"status": "flagged", "shot_id": shot_id, "conflict": conflict}


def log_revision(
    shot_id: str, what_changed: str, why: str, tool_context: ToolContext
) -> dict[str, Any]:
    """Append an entry to the linear revision log (never edits/removes prior ones).

    The `why` is the decision rationale — e.g. the director's reason when they
    override a continuity flag ("badge loss moved to scene 7 for pacing").

    Args:
        shot_id: Shot the revision applies to.
        what_changed: What changed in this revision.
        why: Why it changed — the rationale, required, not optional.
    """
    log = tool_context.state.get("revision_log", [])
    color = REVISION_COLORS[min(len(log), len(REVISION_COLORS) - 1)]
    entry = {
        "rev": len(log) + 1,
        "label": f"Rev. {color}",
        "shot_id": shot_id,
        "what_changed": what_changed,
        "why": why,
    }
    log.append(entry)
    tool_context.state["revision_log"] = log
    _activity(tool_context, "revision-log", f"{entry['label']} — {what_changed}")
    return {"status": "logged", **entry}


def override_continuity_flag(
    shot_id: str, reason: str, tool_context: ToolContext
) -> dict[str, Any]:
    """Approve a flagged shot anyway, recording the reason. Requires confirmation.

    This is the human-in-the-loop gate: the director consciously accepts a
    continuity conflict. The reason is persisted straight into the revision log.

    Args:
        shot_id: The flagged shot to approve.
        reason: Why the conflict is acceptable — becomes the revision rationale.
    """
    shots = tool_context.state.get("shots", [])
    for shot in shots:
        if shot["shot_id"] == shot_id:
            shot["status"] = "approved"
            shot.setdefault("flags", []).append(f"OVERRIDDEN: {reason}")
            break
    tool_context.state["shots"] = shots
    log_revision(shot_id, "Continuity flag overridden by director", reason, tool_context)
    _activity(tool_context, "line-producer", f"override {shot_id}: {reason}")
    return {"status": "approved", "shot_id": shot_id, "reason": reason}


def generate_shot_variants(
    shot_id: str, description: str, camera_notes: str, tool_context: ToolContext
) -> dict[str, Any]:
    """Produce 2-3 rough storyboard variants for a shot (thumbnail-many step).

    Mirrors real storyboarding: fast rough thumbnails first, director picks one,
    then only the survivor gets polished. This is a mock generator returning
    variant descriptors + placeholder frames; swap the body for an Imagen call
    to render real frames.

    Args:
        shot_id: The shot to draft variants for.
        description: Scene/action description to visualise.
        camera_notes: Camera/blocking notes, e.g. "low-angle, wide, night".
    """
    angles = ["wide establishing", "over-the-shoulder", "low-angle close"]
    variants = [
        {
            "variant": i + 1,
            "angle": angle,
            "prompt": f"{description}. Camera: {camera_notes}. Framing: {angle}.",
            "frame": f"placeholder://{shot_id}/v{i + 1}",  # -> Imagen URL later
        }
        for i, angle in enumerate(angles[:3])
    ]
    shots = tool_context.state.get("shots", [])
    for shot in shots:
        if shot["shot_id"] == shot_id:
            shot["variants"] = variants
            shot["status"] = "drafted"
            break
    tool_context.state["shots"] = shots
    _activity(tool_context, "storyboard", f"drafted {len(variants)} variants for {shot_id}")
    return {"status": "ok", "shot_id": shot_id, "variants": variants}


def report_capability_gap(
    agent: str, gap: str, suggested_skill: str, tool_context: ToolContext
) -> dict[str, Any]:
    """Log a structured capability-gap report when an agent hits something it
    can't do — a continuity rule it lacks, a rights check with no clearance
    skill. This is the "gap -> skill request" loop: telemetry, not a forum post.

    Args:
        agent: The agent reporting the gap.
        gap: What it couldn't do.
        suggested_skill: The skill package that would close the gap.
    """
    gaps = tool_context.state.get("capability_gaps", [])
    gaps.append({"agent": agent, "gap": gap, "suggested_skill": suggested_skill})
    tool_context.state["capability_gaps"] = gaps
    _activity(tool_context, agent, f"capability gap: {gap} (needs: {suggested_skill})")
    return {"status": "reported", "gap": gap, "suggested_skill": suggested_skill}


def _request_user_input(message: str) -> dict[str, Any]:
    """Ask the filmmaker a question and pause until they answer.

    Args:
        message: The question or clarification to show the user.
    """
    return {"status": "pending", "message": message}


# Exported tool objects -------------------------------------------------------

upsert_shot_tool = FunctionTool(func=upsert_shot)
flag_shot_tool = FunctionTool(func=flag_shot)
log_revision_tool = FunctionTool(func=log_revision)
# HITL: overriding a continuity flag is a deliberate human decision.
override_flag_tool = FunctionTool(func=override_continuity_flag, require_confirmation=True)
generate_variants_tool = FunctionTool(func=generate_shot_variants)
report_gap_tool = FunctionTool(func=report_capability_gap)
request_user_input_tool = LongRunningFunctionTool(func=_request_user_input)
