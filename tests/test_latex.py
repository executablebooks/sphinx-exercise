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


LATEX_FIGURE = re.compile(
    r"\\begin\{figure\}\[(?P<align>[^\]]*)\](?P<body>.*?)\\end\{figure\}", re.DOTALL
)
# A figure's :name: becomes \label{\detokenize{<docname>:<name>}}
LATEX_FIGURE_NAME = re.compile(r"\\label\{\\detokenize\{[^:}]*:(?P<name>[^}]+)\}\}")


def latex_figures(tex):
    """Map each figure's name to (figure placement, sphinxadmonition depth).

    A figure without a name is collected under None.
    """
    figures = {}
    for figure in LATEX_FIGURE.finditer(tex):
        before = tex[: figure.start()]
        depth = before.count(r"\begin{sphinxadmonition}") - before.count(
            r"\end{sphinxadmonition}"
        )
        name = LATEX_FIGURE_NAME.search(figure["body"])
        figures[name["name"] if name else None] = (figure["align"], depth)
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
        "fig-numbered-exercise": ("H", 1),
        "fig-unnumbered-exercise": ("H", 1),
        "fig-solution": ("H", 1),
        "fig-gated-exercise": ("H", 1),
        "fig-gated-solution": ("H", 1),
        # Figures after the boxes float again, so the counter was restored
        "fig-outside": ("htbp", 0),
        # A code-cell output with mystnb figure metadata in a gated solution
        "fig-code-cell": ("H", 1),
    }
