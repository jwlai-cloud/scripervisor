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

"""Script/Continuity agent — the digital script supervisor ("scripty").

Its job is cross-referencing, not creativity: break a request into shots, then
compare new content against established canon (pulled from production metadata
via MCP) and flag conflicts — props, wardrobe, eyeline, screen direction,
story-day timeline — across narratively-adjacent shots generated out of order.
"""

from google.adk.agents import Agent

from app.config import MODEL, build_asset_mcp_toolset
from app.tools import (
    flag_shot_tool,
    log_revision_tool,
    report_gap_tool,
    upsert_shot_tool,
)

INSTRUCTION = """
You are the Script/Continuity agent — a digital script supervisor.

Your job is cross-referencing, NOT invention:
1. Break the requested change into concrete shots/beats. Register each with
   `upsert_shot` (status "drafted", agent "script-continuity").
2. For every prop, wardrobe item, character detail, location, or story-day fact
   the request touches, call `metadata_lookup` to pull the established canon
   from the story bible.
3. Compare the request against that canon. If it contradicts an established
   fact (e.g. a prop that was already lost, a night-only location shot in day),
   call `flag_shot` with a precise, human-readable conflict.
4. If a check has no matching canon rule you can apply, call
   `report_capability_gap` describing the gap and the skill that would close it
   — do not guess.

Be specific and cite the scene/story-day you compared against. You do not
generate images and you do not decide overrides — the Line Producer owns the
human-in-the-loop decision. Report your findings back to the Line Producer.
"""

script_continuity = Agent(
    name="script_continuity",
    model=MODEL,
    description=(
        "Cross-references new scene content against established canon (via MCP "
        "production metadata) and flags continuity conflicts. Reasoning only."
    ),
    instruction=INSTRUCTION,
    tools=[
        build_asset_mcp_toolset(tool_filter=["metadata_lookup"]),
        upsert_shot_tool,
        flag_shot_tool,
        log_revision_tool,
        report_gap_tool,
    ],
)
