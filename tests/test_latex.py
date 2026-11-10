import re

from TexSoup import TexSoup
import pytest
import sphinx

# Sphinx 8.1.x (Python 3.10 only) has different XML output than 8.2+
# Use .sphinx8.1 for 8.1.x, .sphinx8 for 8.2+ (the standard)
if sphinx.version_info[0] == 8 and sphinx.version_info[1] == 1:
    SPHINX_VERSION = f".sphinx{sphinx.version_info[0]}.{sphinx.version_info[1]}"
else:
    SPHINX_VERSION = f".sphinx{sphinx.version_info[0]}"


@pytest.mark.sphinx("latex", testroot="simplebook")
def test_latex_build(app, file_regression):
    app.build()
    path_exer_directive = app.outdir / "sphinx-exercisetest.tex"
    assert path_exer_directive.exists()

    # get content markup
    file_content = TexSoup(path_exer_directive.read_text(encoding="utf8"))
    file_regression.check(
        str(file_content.document), extension=f"{SPHINX_VERSION}.tex", encoding="utf8"
    )


LATEX_FIGURE_TOKENS = re.compile(
    r"\\(?P<env>begin|end)\{sphinxadmonition\}"
    r"|\\begin\{figure\}\[(?P<align>[^\]]*)\]"
    r"|\\caption\{(?P<caption>[^}]*)\}"
)


def latex_figures(tex):
    """Map each figure caption to (figure placement, sphinxadmonition depth)."""
    figures = {}
    depth = 0
    pending = None
    for match in LATEX_FIGURE_TOKENS.finditer(tex):
        if match["env"] == "begin":
            depth += 1
        elif match["env"] == "end":
            depth -= 1
        elif match["align"] is not None:
            pending = (match["align"], depth)
        elif pending is not None:
            figures[match["caption"]] = pending
            pending = None
    return figures


@pytest.mark.sphinx("latex", testroot="latexfigure")
def test_latex_figure_in_admonition(app):
    """Figures inside exercise and solution boxes must not float (#94).

    A floating figure environment inside the sphinxadmonition box stops
    LaTeX with "Not in outer par mode".
    """
    app.build()
    tex = (app.outdir / "sphinx-exercisetest.tex").read_text(encoding="utf8")

    assert latex_figures(tex) == {
        "Figure in a numbered exercise": ("H", 1),
        "Figure in an unnumbered exercise": ("H", 1),
        "Figure in a solution": ("H", 1),
        "Figure in a gated exercise": ("H", 1),
        "Figure in a gated solution": ("H", 1),
        # Figures after the boxes float again, so the counter was restored
        "Figure outside any box": ("htbp", 0),
    }
