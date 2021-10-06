from TexSoup import TexSoup
import pytest


@pytest.mark.sphinx("latex", testroot="simplebook")
def test_latex_build(app, file_regression):
    app.build()
    path_exer_directive = app.outdir / "sphinx-exercisetest.tex"
    assert path_exer_directive.exists()

    # get content markup
    file_content = TexSoup(path_exer_directive.read_text(encoding="utf8"))
    file_regression.check(str(file_content.document), extension=".tex", encoding="utf8")
