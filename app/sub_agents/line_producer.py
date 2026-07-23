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

"""Line Producer — the backend orchestrator.

Owns requirement understanding, shot breakdown, delegation, model/tool choice,
and the human-in-the-loop decisions. This is the agent with a planner attached;
the role-agents report to it. The user never talks to it directly (that's the
Front Desk's job) — this is the answer to "why is this more than a prompt box".
"""

from google.adk.agents import Agent
from google.adk.planners import PlanReActPlanner

from app.config import MODEL
from app.sub_agents.post_production import post_production
from app.sub_agents.script_continuity import script_continuity
from app.sub_agents.storyboard import storyboard
from app.tools import (
    log_revision_tool,
    override_flag_tool,
    request_user_input_tool,
)

INSTRUCTION = """
You are the Line Producer — the crew's orchestrator. You own the plan.

Given a filmmaker's request handed to you by the Front Desk:
1. Understand the requirement and break it into shots/beats.
2. Delegate in this order, transferring to the right role-agent for each part:
   - `script_continuity` FIRST — always continuity-check a change against canon
     before anything is drawn or assembled. Never skip this.
   - `storyboard` — for shots that need visual variants.
   - `post_production` — to retrieve and clear matching assets.
3. If Continuity flags a conflict, do NOT silently proceed. Surface it to the
   filmmaker. If they choose to proceed anyway, use `override_continuity_flag`
   (this asks for explicit confirmation) and capture their reason — that reason
   is the revision rationale.
4. Record meaningful changes with `log_revision`, always with a real "why".
5. Use `request_user_input` whenever you genuinely need a decision or detail
   only the filmmaker can provide.

You decide which agent handles what and in what order. Keep the filmmaker's
intent intact; be explicit about tradeoffs when a continuity conflict forces one.
"""

line_producer = Agent(
    name="line_producer",
    model=MODEL,
    planner=PlanReActPlanner(),
    description=(
        "Orchestrator: owns requirement understanding, shot breakdown, "
        "delegation across the crew, and human-in-the-loop decisions."
    ),
    instruction=INSTRUCTION,
    sub_agents=[script_continuity, storyboard, post_production],
    tools=[override_flag_tool, log_revision_tool, request_user_input_tool],
)
