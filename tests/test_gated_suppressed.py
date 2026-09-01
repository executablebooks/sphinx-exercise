"""HTML builds must not crash when a gated start directive is suppressed.

Start directives return [] for hide_solutions or :hidden:, so the matching
*-end marker is left in the doctree. Those end nodes have no writer visitors.
"""

from bs4 import BeautifulSoup
import pytest


def _build_html(app, docname):
    app.build()
    path = app.outdir / f"{docname}.html"
    assert path.exists(), f"{docname}.html was not written"
    return BeautifulSoup(path.read_text(encoding="utf8"), "html.parser")


@pytest.mark.sphinx(
    "html",
    testroot="gated-suppressed",
    confoverrides={
        "hide_solutions": True,
        "exclude_patterns": ["hidden_solution*", "hidden_exercise*"],
    },
)
def test_hide_solutions_gated_solution_html_build(app):
    """hide_solutions=True with solution-start/solution-end must not crash."""
    soup = _build_html(app, "hide_solutions")

    text = soup.get_text()
    assert "Visible exercise body" in text
    assert "Visible after" in text
    assert soup.select("div.solution") == []
    # Unmatched solution-end must not be written as an extra admonition.
    assert len(soup.select("div.admonition")) == 1
    assert soup.select("div.exercise")


@pytest.mark.sphinx(
    "html",
    testroot="gated-suppressed",
    confoverrides={"exclude_patterns": ["hide_solutions*", "hidden_exercise*"]},
)
def test_hidden_gated_solution_html_build(app):
    """:hidden: on solution-start/solution-end must not crash."""
    soup = _build_html(app, "hidden_solution")

    text = soup.get_text()
    assert "Visible exercise body" in text
    assert "Visible after" in text
    assert soup.select("div.solution") == []
    assert len(soup.select("div.admonition")) == 1
    assert soup.select("div.exercise")


@pytest.mark.sphinx(
    "html",
    testroot="gated-suppressed",
    confoverrides={"exclude_patterns": ["hide_solutions*", "hidden_solution*"]},
)
def test_hidden_gated_exercise_html_build(app):
    """:hidden: on exercise-start/exercise-end must not crash."""
    soup = _build_html(app, "hidden_exercise")

    text = soup.get_text()
    assert "Visible after" in text
    assert soup.select("div.exercise") == []
    # Unmatched exercise-end must not be written as an empty admonition.
    assert soup.select("div.admonition") == []
