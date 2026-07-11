# Animate Anything — living-list build. Contributors edit README.md; these regenerate the rest.
.PHONY: build fresh
build:  ## recompile the knowledge graph + interactive map from README.md
	python3 scripts/awesome_kg.py build README.md --out knowledge/graph.json \
	  --html docs/index.html --enrich knowledge/enrichments.json --title "Awesome Animation"
fresh:  ## probe every README link for rot
	python3 scripts/check_freshness.py README.md
