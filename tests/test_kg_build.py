"""The knowledge fold, gate-checked: README → graph → llms.txt is one deterministic
compile, and the graph that comes out is structurally sound (every edge endpoint
exists, ids unique, the ranked columns — tier/license — survive into the nodes).
"""
import json

import awesome_kg
from conftest import REPO


def build_real():
    md = (REPO / "README.md").read_text()
    enrich = json.loads((REPO / "knowledge" / "enrichments.json").read_text())
    return awesome_kg.build(md, "Awesome Animation", enrich)


# ── structural integrity: what OpenSpace's validator does for skills, done for the graph ──

def test_graph_integrity():
    g = build_real()
    ids = [n["id"] for n in g["nodes"]]
    assert len(ids) == len(set(ids)), "duplicate node ids"
    idset = set(ids)
    for e in g["edges"]:
        assert e["src"] in idset and e["dst"] in idset, f"dangling edge {e}"
    assert g["stats"]["nodes"] == len(g["nodes"])
    assert g["stats"]["edges"] == len(g["edges"])


def test_registry_scale_and_membership():
    g = build_real()
    repos = [n for n in g["nodes"] if n["type"] == "repo"]
    assert len(repos) >= 40, f"registry collapsed: only {len(repos)} repo nodes"
    linked = {e["src"] for e in g["edges"] if e["type"] == "part_of"}
    orphans = [n["id"] for n in repos if n["id"] not in linked]
    assert not orphans, f"repo nodes without a category: {orphans}"


def test_curator_lineage_survives_regeneration():
    g = build_real()
    assert any(e["type"] == "builds_on" for e in g["edges"]), \
        "enrichments.json builds_on edges were dropped by the rebuild"


# ── the ranked columns are the registry's value — they must reach the graph ──

def test_tier_license_rank_captured():
    g = build_real()
    gsap = next(n for n in g["nodes"] if n["id"] == "repo:gsap")
    assert gsap.get("tier", "").startswith("🥇")
    assert gsap.get("rank") == 1
    assert "GSAP" in gsap.get("license", ""), "License column lost at compile time"
    tiered = [n for n in g["nodes"] if n["type"] == "repo" and n.get("rank")]
    assert len(tiered) >= 30, "most registry rows carry a medal tier"


# ── llms.txt is compiled, ranked, and priced — never hand-maintained ──

def test_llms_txt_renders_from_graph():
    txt = awesome_kg.render_llms(build_real())
    assert "GENERATED from README.md" in txt
    assert "## 🌊 Web / JS animation" in txt
    gsap_line = next(l for l in txt.splitlines() if "GSAP]" in l)
    assert gsap_line.startswith("- 🥇 GSAP —") and "·" in gsap_line, gsap_line
    assert "Learn — the map" not in txt, "taxonomy prose tables don't belong in the tool index"


def test_llms_txt_covers_every_linked_registry_row():
    g = build_real()
    txt = awesome_kg.render_llms(g)
    missing = [n["name"] for n in g["nodes"]
               if n["type"] == "repo" and n.get("links") and n["links"][0] not in txt]
    assert not missing, f"tools in the graph but not the agent index: {missing}"
