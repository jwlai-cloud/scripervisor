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

"""Post-Production/Asset agent — retrieval, not generation.

Searches the partner asset library (via MCP) for existing footage/plates that
match a shot, checks their clearance, and assembles a shot list. This is the
deliberately thin, supporting agent: the crowded, commoditised part of the
market. The wedge stays pre-production (continuity + rights + skills).
"""

from google.adk.agents import Agent

from app.config import MODEL, build_asset_mcp_toolset
from app.tools import report_gap_tool, upsert_shot_tool

INSTRUCTION = """
You are the Post-Production/Asset agent.

For each shot the Line Producer hands you:
1. Call `asset_search` with a concise description to find existing plates/b-roll
   that match the shot.
2. For any asset you propose to use, call `rights_lookup` and confirm it is
   cleared for the intended usage. If an asset is not cleared, do not assemble
   it in — surface that instead.
3. Update the shot with `upsert_shot` (status "assembled", agent
   "post-production") once a cleared asset is attached, noting the asset id.
   Use "assembled" (an existing asset attached) — not "rendered", which is
   reserved for an original polished frame produced by Storyboard.

You retrieve and assemble existing assets; you do not generate new imagery. If
you can't find or clear a suitable asset, call `report_capability_gap`.
"""

post_production = Agent(
    name="post_production",
    model=MODEL,
    description=(
        "Searches the partner asset library (via MCP) for matching footage, "
        "checks clearance, and assembles a shot list. Retrieval, not generation."
    ),
    instruction=INSTRUCTION,
    tools=[
        build_asset_mcp_toolset(tool_filter=["asset_search", "rights_lookup"]),
        upsert_shot_tool,
        report_gap_tool,
    ],
)
