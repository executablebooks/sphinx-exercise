"""Tests for the ``solution_collapsed`` configuration option.

``solution_collapsed = True`` adds the ``dropdown`` class to every solution
directive so that solutions render folded by default. The class is consumed by
sphinx-togglebutton, whose default selector is ``.toggle, .admonition.dropdown``.
"""

import importlib.util

import pytest
from bs4 import BeautifulSoup

HAS_TOGGLEBUTTON = importlib.util.find_spec("sphinx_togglebutton") is not None


def get_solution_classes(app, docname):
    """Return the class list of the first ``div.solution`` in a built page."""
    path = app.outdir / docname
    assert path.exists(), f"{docname} was not built"
    soup = BeautifulSoup(path.read_text(encoding="utf8"), "html.parser")
    solutions = soup.select("div.solution")
    assert solutions, f"no solution directive found in {docname}"
    return solutions[0].get("class", [])


@pytest.mark.sphinx(
    "html", testroot="mybook", confoverrides={"solution_collapsed": True}
)
def test_solution_collapsed_adds_dropdown_class(app):
    """solution_collapsed=True adds the 'dropdown' class to a solution."""
    app.build()
    classes = get_solution_classes(app, "solution/_linked_enum.html")
    assert "dropdown" in classes, f"expected 'dropdown' in {classes}"
    assert "solution" in classes, "the 'solution' class must be preserved"


@pytest.mark.sphinx("html", testroot="mybook")
def test_solution_collapsed_default_is_off(app):
    """By default no 'dropdown' class is added (backwards compatibility)."""
    app.build()
    classes = get_solution_classes(app, "solution/_linked_enum.html")
    assert "dropdown" not in classes, (
        "solution_collapsed defaults to False so no 'dropdown' class should be "
        f"added, got {classes}"
    )


@pytest.mark.sphinx(
    "html", testroot="mybook", confoverrides={"solution_collapsed": True}
)
def test_solution_collapsed_preserves_custom_class(app):
    """A directive-level :class: is kept alongside the injected 'dropdown'."""
    app.build()
    classes = get_solution_classes(app, "solution/_linked_enum_class.html")
    assert "dropdown" in classes, f"expected 'dropdown' in {classes}"
    assert (
        "test-solution" in classes
    ), f"the author's :class: value must be preserved, got {classes}"


@pytest.mark.sphinx(
    "html", testroot="mybook", confoverrides={"solution_collapsed": True}
)
def test_solution_collapsed_no_duplicate_dropdown(app):
    """An explicit ':class: dropdown' is not duplicated by the config option."""
    app.build()
    classes = get_solution_classes(app, "solution/_linked_enum_dropdown.html")
    assert (
        classes.count("dropdown") == 1
    ), f"'dropdown' should appear exactly once, got {classes}"


@pytest.mark.sphinx("html", testroot="mybook")
def test_solution_collapsed_off_keeps_explicit_dropdown(app):
    """':class: dropdown' keeps working when the config option is off."""
    app.build()
    classes = get_solution_classes(app, "solution/_linked_enum_dropdown.html")
    assert (
        "dropdown" in classes
    ), f"an explicit ':class: dropdown' must still be honoured, got {classes}"


@pytest.mark.sphinx(
    "html", testroot="gateddirective", confoverrides={"solution_collapsed": True}
)
def test_solution_collapsed_gated_directive(app):
    """Gated solution-start/solution-end pairs are collapsed too.

    The class list is rebuilt by ``MergeGatedSolutions`` when the pair is merged
    into a single solution node, so this guards against the injected class being
    dropped in the process.
    """
    app.build()
    classes = get_solution_classes(app, "solution-exercise-gated.html")
    assert (
        "dropdown" in classes
    ), f"gated solutions should also be collapsed, got {classes}"


@pytest.mark.sphinx(
    "html", testroot="mybook", confoverrides={"solution_collapsed": True}
)
def test_solution_collapsed_warns_without_togglebutton(app, warnings):
    """A warning is emitted when no extension implements the dropdown class.

    The 'mybook' test root does not load sphinx-togglebutton, so the injected
    class would be inert and the solutions would silently render expanded.
    """
    app.build()
    assert "solution_collapsed=True requires 'sphinx_togglebutton'" in warnings(app)


@pytest.mark.skipif(not HAS_TOGGLEBUTTON, reason="sphinx-togglebutton is not installed")
@pytest.mark.sphinx(
    "html",
    testroot="mybook",
    confoverrides={
        "solution_collapsed": True,
        "extensions": ["sphinx_exercise", "myst_nb", "sphinx_togglebutton"],
    },
)
def test_solution_collapsed_no_warning_with_togglebutton(app, warnings):
    """No warning when sphinx-togglebutton is loaded."""
    app.build()
    assert "solution_collapsed=True requires" not in warnings(app)


@pytest.mark.sphinx(
    "latex", testroot="mybook", confoverrides={"solution_collapsed": True}
)
def test_solution_collapsed_no_warning_for_latex(app, warnings):
    """Non-HTML builders render solutions inline, so no warning is emitted."""
    app.build()
    assert "solution_collapsed=True requires" not in warnings(app)
