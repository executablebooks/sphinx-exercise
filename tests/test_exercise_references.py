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
        "_enum_ref_mathtitle.html",
        "_enum_ref_notitle.html",
        "_enum_ref_title.html",
        "_enum_numref_mathtitle.html",
        "_enum_numref_notitle.html",
        "_enum_numref_title.html",
        "_unenum_ref_mathtitle.html",
        "_unenum_ref_notitle.html",
        "_unenum_ref_title.html",
        "_unenum_numref_mathtitle.html",
        "_unenum_numref_notitle.html",
        "_unenum_numref_title.html",
        "_enum_numref_placeholders.html",
    ],
)
def test_reference(app, idir, file_regression):
    """Test exercise ref and numref role markup."""
    app.builder.build_all()
    path_exc_directive = app.outdir / "exercise" / idir
    assert path_exc_directive.exists()
    # get content markup
    soup = BeautifulSoup(path_exc_directive.read_text(encoding="utf8"), "html.parser")

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
        "_enum_numref_mathtitle",
        "_enum_numref_notitle",
        "_enum_numref_placeholders",
        "_enum_numref_title",
        "_enum_ref_mathtitle",
        "_enum_ref_notitle",
        "_enum_ref_title",
        "_unenum_numref_mathtitle",
        "_unenum_numref_notitle",
        "_unenum_numref_title",
        "_unenum_ref_mathtitle",
        "_unenum_ref_notitle",
        "_unenum_ref_title",
    ],
)
def test_exercise_doctree(app, docname, file_regression, get_sphinx_app_doctree):
    app.build()
    docname = "exercise" + "/" + docname
    get_sphinx_app_doctree(
        app,
        docname,
        resolve=False,
        regress=True,
        flatten_outdir=True,  # noqa: E501 flatten files "solution/<file> -> <file>.xml" for convenience
    )
