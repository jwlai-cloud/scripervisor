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

"""Central config for the Scripervisor crew.

The one place that knows *where* production data comes from. Swapping the mock
MCP server for the real partner endpoint (announced the week of Jul 27) is a
change to `PARTNER_MCP_URL` here — not a re-architecture of any agent.
"""

import os
import sys
from pathlib import Path

from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import (
    SseConnectionParams,
    StdioConnectionParams,
)
from mcp import StdioServerParameters

# Single model knob for the whole crew. Reasoning/routing agents share it;
# the Storyboard agent will point image generation at Imagen separately.
MODEL = os.getenv("SCRIPERVISOR_MODEL", "gemini-flash-latest")

# When the partner MCP server is announced, set PARTNER_MCP_URL and every asset
# agent talks to the real thing. Until then, each McpToolset launches the local
# mock server over stdio.
PARTNER_MCP_URL = os.getenv("PARTNER_MCP_URL")

_MOCK_SERVER = Path(__file__).resolve().parent.parent / "mcp_server" / "mock_server.py"


def build_asset_mcp_toolset(tool_filter: list[str] | None = None) -> McpToolset:
    """Return an McpToolset wired to the partner MCP server, or the local mock.

    `tool_filter` restricts which MCP tools this agent may see, so Continuity
    gets metadata lookups while Post-Production gets asset search — same server,
    least-privilege slices.
    """
    if PARTNER_MCP_URL:
        return McpToolset(
            connection_params=SseConnectionParams(url=PARTNER_MCP_URL),
            tool_filter=tool_filter,
        )
    return McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command=sys.executable,
                args=[str(_MOCK_SERVER)],
            ),
        ),
        tool_filter=tool_filter,
    )
