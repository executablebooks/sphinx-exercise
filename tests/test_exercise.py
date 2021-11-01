from bs4 import BeautifulSoup
import pytest


@pytest.mark.sphinx("html", testroot="mybook")
@pytest.mark.parametrize(
    "idir",
    [
        "_enum_mathtitle_label.html",
        "_enum_notitle_label.html",
        "_enum_title_class_label.html",
        "_enum_title_nolabel.html",
        "_unenum_mathtitle_label.html",
        "_unenum_notitle_label.html",
        "_unenum_title_class_label.html",
        "_unenum_title_nolabel.html",
    ],
)
def test_exercise(app, idir, file_regression):
    """Test exercise directive markup."""
    app.build()
    path_exc_directive = app.outdir / "exercise" / idir
    assert path_exc_directive.exists()

    # get content markup
    soup = BeautifulSoup(path_exc_directive.read_text(encoding="utf8"), "html.parser")
    excs = soup.select("div.exercise")[0]
    file_regression.check(str(excs), basename=idir.split(".")[0], extension=".html")


@pytest.mark.sphinx("html", testroot="mybook")
@pytest.mark.parametrize(
    "docname",
    [
        "_enum_duplicate_label",
        "_enum_mathtitle_label",
        "_enum_notitle_label",
        "_enum_numref_mathtitle",
        "_enum_numref_notitle",
        "_enum_numref_placeholders",
        "_enum_numref_title",
        "_enum_ref_mathtitle",
        "_enum_ref_notitle",
        "_enum_ref_title",
        "_enum_title_class_label",
        "_enum_title_nolabel",
        "_unenum_mathtitle_label",
        "_unenum_notitle_label",
        "_unenum_numref_mathtitle",
        "_unenum_numref_notitle",
        "_unenum_numref_title",
        "_unenum_ref_mathtitle",
        "_unenum_ref_notitle",
        "_unenum_ref_title",
        "_unenum_title_class_label",
        "_unenum_title_nolabel",
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
        str(excs[:-1]), basename=idir.split(".")[0], extension=".html"
    )
