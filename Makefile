# Animate Anything — living-list build. Contributors edit README.md; these regenerate the rest.
.PHONY: build fresh check agentic
build:  ## recompile the knowledge graph + interactive map + agent index from README.md
	python3 scripts/awesome_kg.py build README.md --out knowledge/graph.json \
	  --html docs/index.html --llms llms.txt \
	  --enrich knowledge/enrichments.json --enrich knowledge/agentic.json \
	  --title "Awesome Animation"
fresh:  ## probe every README link for rot
	python3 scripts/check_freshness.py README.md
agentic:  ## re-probe the observed agentic surface (AGENTS.md/skills/plugins/MCP) of 🥇 repos
	python3 scripts/agentic_probe.py && $(MAKE) build
check:  ## the finish line — style-linter + knowledge-graph gates (stdlib + pytest, no manim needed)
	python3 -m pytest tests/ -q
	python3 scripts/animate.py lint examples/odd_squares.py --gate 80
	python3 scripts/animate.py lint examples/geometric_series.py --gate 80
