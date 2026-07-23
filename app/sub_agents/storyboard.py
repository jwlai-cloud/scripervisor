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

"""Storyboard agent — thumbnail-many, pick-one, polish-one.

Real storyboard artists draft several rough thumbnails per shot (deliberately
disposable), get director notes, then polish only the survivor. This agent
mirrors that: generate 2-3 rough variants per shot, let the human pick on the
Shot Board, and only then render the polished frame — controlling cost and
directly addressing the character-consistency weakness of one-shot generators.
"""

from google.adk.agents import Agent

from app.config import MODEL
from app.tools import generate_variants_tool, report_gap_tool, upsert_shot_tool

INSTRUCTION = """
You are the Storyboard agent.

For each shot the Line Producer hands you:
1. Call `generate_shot_variants` with the scene description and camera/blocking
   notes to produce 2-3 rough variant compositions (different angles). These are
   fast, rough, disposable — the point is to give the director choices, not a
   locked-in frame.
2. Register/refresh the shot with `upsert_shot` so the board shows the variants.
3. Do NOT pick the winning variant yourself — that is the human's choice on the
   Shot Board. Once a variant is chosen, a later polish pass renders it cleanly.

If a shot needs a capability you don't have (e.g. a reference-image-anchored
character-consistency pass), call `report_capability_gap` naming the skill that
would close it. Keep prompts concrete about framing, lens, and lighting.
"""

storyboard = Agent(
    name="storyboard",
    model=MODEL,
    description=(
        "Generates 2-3 rough storyboard variants per shot (still frames) for the "
        "director to pick from, then polishes the chosen one."
    ),
    instruction=INSTRUCTION,
    tools=[generate_variants_tool, upsert_shot_tool, report_gap_tool],
)
