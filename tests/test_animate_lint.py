"""The /animate-anything skill's own gates, tested.

Discipline (from OpenSpace's evolution engine): machine-generated artifacts pass a
deterministic validator BEFORE anything trusts them — and the validator itself is
what these tests pin down. Golden examples are the evidence corpus: if the linter
or an example drifts, this fails loud (never skips).
"""
import animate
from conftest import REPO


def lint(src: str):
    score, checks = animate._lint(src)
    return score, {cid: ok for cid, ok, _ in checks}


# ── golden examples: the committed evidence must keep scoring what the README claims ──

def test_golden_odd_squares_scores_100():
    src = (REPO / "examples" / "odd_squares.py").read_text()
    score, _ = lint(src)
    assert score == 100, "odd_squares.py is the documented 100/100 golden reference"


def test_golden_geometric_series_passes_ci_gate():
    src = (REPO / "examples" / "geometric_series.py").read_text()
    score, _ = lint(src)
    assert score >= 80, "geometric_series.py must clear the same --gate 80 CI enforces"


# ── scaffold self-validation: what we emit must pass our own gate (admission, not vibes) ──

def test_scaffold_output_passes_its_own_gate():
    code = animate._SCAFFOLD.format(concept="eigenvectors", name="EigenvectorsScene", stem="scene")
    score, checks = lint(code)
    assert score >= 80, f"scaffold emits code failing its own linter ({score}/100)"
    assert checks["warm-grey-canvas"] and checks["morph-to-equivalence"]


def test_scaffold_class_name_slug():
    assert animate.slugify("the fourier transform, visually!") == "TheFourierTransformVisuallyScene"
    assert animate.slugify("") == "ExplainerScene"


# ── the contract's teeth: each anti-tell actually trips ──

BASE = "from manim import *\nclass S(Scene):\n    def construct(self):\n"


def test_pure_black_canvas_fails_the_number_one_tell():
    src = BASE + 'config.background_color = "#000000"\n'
    _, checks = lint(src)
    assert not checks["warm-grey-canvas"]


def test_warm_grey_canvas_passes():
    src = 'config.background_color = "#333333"\n' + BASE
    _, checks = lint(src)
    assert checks["warm-grey-canvas"]


def test_fadeout_fadein_of_equations_flagged_as_missed_morph():
    src = BASE + (
        "        self.play(FadeOut(old_formula_tex))\n"
        "        self.play(FadeIn(new_formula_tex))\n"
    )
    _, checks = lint(src)
    assert not checks["no-missed-morph"], "FadeOut→FadeIn of a formula is the AI-slop tell"


def test_manimlib_import_rejected():
    src = "from manimlib import *\nclass S(Scene):\n    def construct(self):\n        pass\n"
    _, checks = lint(src)
    assert not checks["community-target"]


def test_gate_exit_codes(tmp_path):
    bad = tmp_path / "bad.py"
    bad.write_text("print('not a scene')\n")
    assert animate.main(["lint", str(bad), "--gate", "80"]) == 1
    good = tmp_path / "good.py"
    good.write_text((REPO / "examples" / "odd_squares.py").read_text())
    assert animate.main(["lint", str(good), "--gate", "80"]) == 0
