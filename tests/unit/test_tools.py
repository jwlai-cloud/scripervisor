# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License").
# See the LICENSE file in the project root for the full license text.

"""Unit tests for the crew's shared state tools (no network / no LLM).

The tools only touch `tool_context.state`, so a stub with a `.state` dict is
enough to exercise the real logic.
"""

from types import SimpleNamespace

from app.tools import (
    flag_shot,
    generate_shot_variants,
    log_revision,
    override_continuity_flag,
    upsert_shot,
)


def ctx() -> SimpleNamespace:
    return SimpleNamespace(state={})


def test_upsert_is_idempotent_by_shot_id() -> None:
    c = ctx()
    upsert_shot("S1", "night scene", "drafted", "storyboard", c)
    upsert_shot("S1", "night scene v2", "flagged", "script-continuity", c)
    assert len(c.state["shots"]) == 1
    assert c.state["shots"][0]["status"] == "flagged"
    assert c.state["shots"][0]["scene"] == "night scene v2"


def test_revision_labels_follow_wga_colour_sequence() -> None:
    c = ctx()
    r1 = log_revision("S1", "initial breakdown", "from request", c)
    r2 = log_revision("S1", "second pass", "director note", c)
    assert r1["label"] == "Rev. White"
    assert r2["label"] == "Rev. Blue"
    assert [e["rev"] for e in c.state["revision_log"]] == [1, 2]


def test_override_approves_shot_and_persists_rationale() -> None:
    c = ctx()
    upsert_shot("S1", "scene", "drafted", "script-continuity", c)
    flag_shot("S1", "badge already lost in Scene 4", "script-continuity", c)
    assert c.state["shots"][0]["status"] == "flagged"

    res = override_continuity_flag("S1", "moved badge loss to scene 7 for pacing", c)
    assert res["status"] == "approved"
    assert c.state["shots"][0]["status"] == "approved"
    # The override reason must land in the linear revision log as the rationale.
    assert any("pacing" in e["why"] for e in c.state["revision_log"])


def test_storyboard_generates_two_to_three_variants() -> None:
    c = ctx()
    upsert_shot("S1", "night alley", "drafted", "storyboard", c)
    res = generate_shot_variants("S1", "night alley chase", "low-angle wide", c)
    assert 2 <= len(res["variants"]) <= 3
    assert c.state["shots"][0]["variants"] == res["variants"]


def test_generating_variants_does_not_regress_an_approved_shot() -> None:
    # Status is a state machine: re-drafting variants must not knock an already
    # approved shot back to "drafted".
    c = ctx()
    upsert_shot("S1", "night alley", "approved", "line-producer", c)
    generate_shot_variants("S1", "night alley chase", "low-angle wide", c)
    assert c.state["shots"][0]["status"] == "approved"
    assert len(c.state["shots"][0]["variants"]) == 3
