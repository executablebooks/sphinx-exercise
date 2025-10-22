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
