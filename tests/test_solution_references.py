from bs4 import BeautifulSoup
import pytest
import sphinx

# Sphinx 8.1.x (Python 3.10 only) has different XML output than 8.2+
# Use .sphinx8.1 for 8.1.x, .sphinx8 for 8.2+ (the standard)
if sphinx.version_info[0] == 8 and sphinx.version_info[1] == 1:
    SPHINX_VERSION = f".sphinx{sphinx.version_info[0]}.{sphinx.version_info[1]}"
else:
    SPHINX_VERSION = f".sphinx{sphinx.version_info[0]}"


@pytest.mark.sphinx("html", testroot="mybook")
@pytest.mark.parametrize(
    "idir",
    [
        "_linked_ref_enum.html",
        "_linked_ref_unenum_mathtitle.html",
        "_linked_ref_unenum_mathtitle2.html",
        "_linked_ref_unenum_notitle.html",
        "_linked_ref_unenum_title.html",
    ],
)
def test_reference(app, idir, file_regression):
    """Test solution ref role markup."""
    app.builder.build_all()
    path_solution_directive = app.outdir / "solution" / idir
    assert path_solution_directive.exists()
    # get content markup
    soup = BeautifulSoup(
        path_solution_directive.read_text(encoding="utf8"), "html.parser"
    )

    excs = ""
    all_refs = soup.select("p")
    for ref in all_refs:
        excs += f"{ref}\n"

    file_regression.check(
        str(excs[:-1]), basename=idir.split(".")[0], extension=f"{SPHINX_VERSION}.html"
    )


@pytest.mark.sphinx("html", testroot="mybook")
@pytest.mark.parametrize(
    "docname",
    [
        "_linked_ref_enum",
        "_linked_ref_unenum_mathtitle",
        "_linked_ref_unenum_mathtitle2",
        "_linked_ref_unenum_notitle",
        "_linked_ref_unenum_title",
        "_linked_ref_wronglabel",
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
    )
