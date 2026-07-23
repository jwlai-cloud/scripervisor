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

"""Front Desk — the user-facing agent. A mover, not a creator.

It takes the filmmaker's plain-English request, does light validation, and
hands off to the Line Producer. It has NO planning authority: it does not
decide shot breakdown, workflow order, model choice, or write generation
prompts. Deliberately the only chat-like surface in the product.
"""

from google.adk.agents import Agent

from app.config import MODEL
from app.sub_agents.line_producer import line_producer
from app.tools import request_user_input_tool

INSTRUCTION = """
You are the Front Desk at a film production studio.

Your ONLY job:
1. Take the filmmaker's request in plain English.
2. Do light validation — if the request is too vague to act on at all, use
   `request_user_input` to ask one clarifying question.
3. Confirm in a single sentence what you understood, then transfer to the
   `line_producer`, who owns everything from here.

You do NOT break requests into shots, choose an order, pick models, or write
generation prompts. You have no creative or technical authority. Hand off.
"""

front_desk = Agent(
    name="front_desk",
    model=MODEL,
    description=(
        "User-facing intake. Collects the filmmaker's request, lightly validates "
        "it, and hands off to the Line Producer. No planning authority."
    ),
    instruction=INSTRUCTION,
    sub_agents=[line_producer],
    tools=[request_user_input_tool],
)
