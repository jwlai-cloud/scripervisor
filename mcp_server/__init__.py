# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License").
# See the LICENSE file in the project root for the full license text.

"""Local mock MCP server standing in for the hackathon partner's MCP endpoint.

The real partner + server domain is announced the week of Jul 27; until then
this exposes asset-search / metadata-lookup / rights-lookup shaped tools so the
crew can be built and demoed end to end. Swap it out via `PARTNER_MCP_URL`.
"""
