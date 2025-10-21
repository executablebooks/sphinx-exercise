from bs4 import BeautifulSoup
import pytest
import sphinx

SPHINX_VERSION = f".sphinx{sphinx.version_info[0]}"


@pytest.mark.sphinx("html", testroot="mybook")
@pytest.mark.parametrize(
    "idir",
    [
        "_linked_enum.html",
        "_linked_enum_class.html",
        "_linked_unenum_mathtitle.html",
        "_linked_unenum_mathtitle2.html",
        "_linked_unenum_notitle.html",
        "_linked_unenum_title.html",
        "_linked_wrong_targetlabel.html",
    ],
)
def test_solution(app, idir, file_regression):
    """Test solution directive markup."""
    app.build()
    path_solution_directive = app.outdir / "solution" / idir
    assert path_solution_directive.exists()

    # get content markup
    soup = BeautifulSoup(
        path_solution_directive.read_text(encoding="utf8"), "html.parser"
    )

    sol = soup.select("div.solution")[0]
    file_regression.check(str(sol), basename=idir.split(".")[0], extension=".html")


@pytest.mark.sphinx("html", testroot="mybook")
@pytest.mark.parametrize(
    "docname",
    [
        "_linked_duplicate_label",
        "_linked_enum",
        "_linked_enum_class",
        "_linked_missing_arg",
        "_linked_unenum_mathtitle",
        "_linked_unenum_mathtitle2",
        "_linked_unenum_notitle",
        "_linked_unenum_title",
        "_linked_wrong_targetlabel",
    ],
)
def test_solution_doctree(app, docname, file_regression, get_sphinx_app_doctree):
    app.build()
    docname = "solution" + "/" + docname
    get_sphinx_app_doctree(
        app,
        docname,
        resolve=False,
        regress=True,
        flatten_outdir=True,  # noqa: E501 flatten files "solution/<file> -> <file>.xml" for convenience
        sphinx_version=SPHINX_VERSION,
    )
