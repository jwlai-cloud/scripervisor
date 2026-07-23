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

"""Scripervisor crew entrypoint.

Assembles the org chart:

    Front Desk (root, router)
      └─ Line Producer (orchestrator, planner)
           ├─ Script/Continuity
           ├─ Storyboard
           └─ Post-Production/Asset  ── MCP ──> partner server (mock for now)
"""

import os

import google.auth
from google.adk.apps import App

from app.sub_agents.front_desk import front_desk

# Vertex AI wiring — matches the scaffold's default (project auto-detected).
_, project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id or "")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

root_agent = front_desk

# App name must match the package directory ("app") for the scaffold tooling.
app = App(
    root_agent=root_agent,
    name="app",
)
