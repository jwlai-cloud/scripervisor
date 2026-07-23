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

"""Mock MCP server for Scripervisor.

Exposes three tools shaped like the likely partner surface (editorial metadata,
asset search, rights lookup). Run standalone over stdio — ADK's `McpToolset`
launches it via `python mock_server.py`. Canned data is deliberately built
around the demo: a detective who already lost her badge in Scene 4.

# ponytail: in-memory dicts, not a DB. That's the whole point of a mock — the
# real data comes from the partner server. Keep this dumb and swappable.
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("scripervisor-mock-assets")

# --- Canon: the "story bible" a script supervisor cross-references against ----
_STORY_BIBLE = {
    "badge": {
        "entity": "detective's badge",
        "status": "lost",
        "established_scene": 4,
        "story_day": 2,
        "note": "Detective Vera loses her badge in Scene 4 (day). It is not "
        "recovered on-screen afterwards.",
    },
    "detective": {
        "entity": "Detective Vera",
        "wardrobe": "grey trench coat, no badge after Scene 4",
        "note": "Left-handed; holds sidearm in left hand for continuity.",
    },
    "warehouse": {
        "entity": "riverside warehouse",
        "note": "Established as night-only location. No daytime interiors exist.",
    },
}

# --- Asset library: existing footage/plates the crew can retrieve -------------
_ASSETS = [
    {
        "asset_id": "PLATE-014",
        "kind": "background plate",
        "description": "Rain-slick city street at night, neon signage",
        "tags": ["night", "city", "rain", "exterior"],
        "duration_s": 12,
    },
    {
        "asset_id": "PLATE-021",
        "kind": "background plate",
        "description": "Warehouse interior, moonlight through high windows",
        "tags": ["night", "warehouse", "interior", "moody"],
        "duration_s": 8,
    },
    {
        "asset_id": "BROLL-103",
        "kind": "b-roll",
        "description": "Close-up of hands, empty badge holder",
        "tags": ["insert", "badge", "hands", "close-up"],
        "duration_s": 4,
    },
]

# --- Rights: clearance status per asset ---------------------------------------
_RIGHTS = {
    "PLATE-014": {"license": "stock-perpetual", "cleared": True, "territory": "worldwide"},
    "PLATE-021": {"license": "in-house", "cleared": True, "territory": "worldwide"},
    "BROLL-103": {
        "license": "editorial-only",
        "cleared": False,
        "note": "Editorial-only license — not cleared for commercial release.",
    },
}


@mcp.tool()
def metadata_lookup(entity: str) -> dict:
    """Look up an established canon fact from the production's story bible.

    Args:
        entity: Keyword for the entity/prop, e.g. "badge", "detective".

    Returns:
        The canon record, or a miss with the known keys.
    """
    key = entity.strip().lower()
    for k, record in _STORY_BIBLE.items():
        if k in key or key in k:
            return {"found": True, "entity": k, "record": record}
    return {"found": False, "query": entity, "known_entities": list(_STORY_BIBLE)}


@mcp.tool()
def asset_search(query: str) -> dict:
    """Search the partner asset library for footage/plates matching a query.

    Args:
        query: Free-text description, e.g. "night city street".

    Returns:
        Ranked matching assets (naive keyword overlap for the mock).
    """
    terms = {t for t in query.strip().lower().replace(",", " ").split() if t}
    scored = []
    for asset in _ASSETS:
        haystack = set(asset["tags"]) | set(asset["description"].lower().split())
        overlap = len(terms & haystack)
        if overlap:
            scored.append((overlap, asset))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return {"query": query, "results": [asset for _, asset in scored]}


@mcp.tool()
def rights_lookup(asset_id: str) -> dict:
    """Look up licensing/clearance status for an asset.

    Args:
        asset_id: The asset id, e.g. "PLATE-014".

    Returns:
        Clearance record, or a miss.
    """
    record = _RIGHTS.get(asset_id.strip().upper())
    if record is None:
        return {"found": False, "asset_id": asset_id, "known": list(_RIGHTS)}
    return {"found": True, "asset_id": asset_id.strip().upper(), "rights": record}


if __name__ == "__main__":
    # stdio transport — the shape ADK's StdioConnectionParams expects.
    mcp.run()
