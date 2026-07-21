"""The agentic-surface layer: annotation-merge semantics, the probed overlay's
integrity against the real graph, and the offline classification logic of the
prober (network probing itself is CI's job — these tests stay hermetic).
"""
import json

import agentic_probe
import awesome_kg
from conftest import REPO


# ── merge(): existing id = annotate (fill, never overwrite); new id = append ──

def test_merge_annotates_existing_node_without_overwriting():
    g = {"kind": "awesome", "subject": "t",
         "nodes": [{"id": "repo:x", "type": "repo", "name": "X", "links": [], "tier": "🥇"}],
         "edges": []}
    awesome_kg.merge(g, {"nodes": [{"id": "repo:x", "tier": "🥉", "agentic": ["agents-md"]}]})
    n = g["nodes"][0]
    assert n["tier"] == "🥇", "overlay must not overwrite README-derived truth"
    assert n["agentic"] == ["agents-md"], "overlay must fill fields the node lacks"
    assert len(g["nodes"]) == 1


def test_merge_still_appends_new_nodes_and_edges():
    g = {"kind": "awesome", "subject": "t",
         "nodes": [{"id": "repo:x", "type": "repo", "name": "X", "links": []}], "edges": []}
    awesome_kg.merge(g, {"nodes": [{"id": "repo:y", "type": "repo", "name": "Y"}],
                         "edges": [{"src": "repo:y", "dst": "repo:x", "type": "builds_on"}]})
    assert len(g["nodes"]) == 2 and len(g["edges"]) == 1


# ── the committed probe overlay stays coherent with the committed graph ──

def test_agentic_overlay_ids_exist_in_graph():
    overlay = json.loads((REPO / "knowledge" / "agentic.json").read_text())
    graph_ids = {n["id"] for n in json.loads((REPO / "knowledge" / "graph.json").read_text())["nodes"]}
    stale = [n["id"] for n in overlay["nodes"] if n["id"] not in graph_ids]
    assert not stale, f"agentic.json annotates nodes no longer in the graph: {stale}"
    for n in overlay["nodes"]:
        assert n.get("agentic_probe", "").startswith("github:"), "every annotation names its evidence source"


def test_graph_carries_agentic_evidence():
    nodes = json.loads((REPO / "knowledge" / "graph.json").read_text())["nodes"]
    hyper = next(n for n in nodes if n["id"] == "repo:heygen-hyperframes")
    assert "agents-md" in hyper.get("agentic", []), "hyperframes' observed AGENTS.md must reach the graph"


# ── llms.txt renders the agentic markers ──

def test_llms_line_carries_agentic_tokens():
    g = {"kind": "awesome", "subject": "t",
         "nodes": [{"id": "category:c", "type": "category", "name": "C", "links": []},
                   {"id": "repo:x", "type": "repo", "name": "X", "links": ["https://e.io"],
                    "summary": "s", "tier": "🥇", "agentic": ["agents-md", "skills-dir"]}],
         "edges": [{"src": "repo:x", "dst": "category:c", "type": "part_of"}]}
    txt = awesome_kg.render_llms(g)
    assert "· agentic: agents-md+skills-dir" in txt


# ── prober classification (offline): root listing → surface tokens ──

def test_probe_surface_classification(monkeypatch):
    listings = {
        "repos/o/r/contents/": [{"name": "AGENTS.md", "type": "file"},
                                {"name": "skills", "type": "dir"},
                                {"name": ".claude", "type": "dir"},
                                {"name": "README.md", "type": "file"}],
        "repos/o/r/contents/.claude": [{"name": "skills", "type": "dir"}],
    }
    monkeypatch.setattr(agentic_probe, "_gh", lambda path: listings[path])
    assert agentic_probe.probe("o/r") == ["agents-md", "claude-skills", "skills-dir"]


def test_probe_gh_slug():
    assert agentic_probe.gh_slug("https://github.com/greensock/GSAP") == "greensock/GSAP"
    assert agentic_probe.gh_slug("https://example.com") == ""
