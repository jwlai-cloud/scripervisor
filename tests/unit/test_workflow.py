# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License").
# See the LICENSE file in the project root for the full license text.

"""Construction test for the ADK 2.0 Workflow graph (no network / no LLM).

Importing `app.workflow` builds the `Workflow`, and ADK runs graph validation
at construction time — reachability, no unconditional cycles (the revise loop
must carry a route), single-turn node mode, and well-formed dict routing. So a
malformed graph fails this test at import.
"""

from google.adk.workflow import Workflow

from app.workflow import scripervisor_graph, workflow_app


def test_graph_constructs_and_validates() -> None:
    assert isinstance(scripervisor_graph, Workflow)
    assert scripervisor_graph.name == "scripervisor_graph"
    assert workflow_app.root_agent is scripervisor_graph
