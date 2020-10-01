from bs4 import BeautifulSoup
import pytest
import shutil


@pytest.mark.sphinx("html", testroot="mybook")
def test_warnings(app, warnings):
    build_path = app.srcdir.joinpath("_build")
    shutil.rmtree(build_path)
    app.build()
    assert (
        "_enum_numref_mathtitle.rst:6: WARNING: invalid numfig_format: some text"
        in warnings(app)
    )
    assert (
        "_enum_numref_notitle.rst:6: WARNING: invalid numfig_format: some text"
        in warnings(app)
    )
    assert (
        "WARNING: invalid numfig_format: some text {name} (KeyError('name'))"
        in warnings(app)
    )
    assert (
        "_enum_numref_title.rst:6: WARNING: invalid numfig_format: some text"
        in warnings(app)
    )
    assert (
        "_unenum_numref_mathtitle.rst:4: WARNING: undefined label: unen-exc-label-math"
        in warnings(app)
    )
    assert (
        "_unenum_numref_mathtitle.rst:6: WARNING: undefined label: unen-exc-label-math"
        in warnings(app)
    )
    assert (
        "_unenum_numref_mathtitle.rst:8: WARNING: undefined label: unen-exc-label-math"
        in warnings(app)
    )
    assert (
        "_unenum_numref_mathtitle.rst:10: WARNING: undefined label: unen-exc-label-math"
        in warnings(app)
    )
    assert (
        "_unenum_numref_mathtitle.rst:12: WARNING: undefined label: unen-exc-label-math"
        in warnings(app)
    )
    assert (
        "_unenum_numref_notitle.rst:4: WARNING: undefined label: unen-exc-notitle"
        in warnings(app)
    )
    assert (
        "_unenum_numref_notitle.rst:6: WARNING: undefined label: unen-exc-notitle"
        in warnings(app)
    )
    assert (
        "_unenum_numref_notitle.rst:8: WARNING: undefined label: unen-exc-notitle"
        in warnings(app)
    )
    assert (
        "_unenum_numref_notitle.rst:10: WARNING: undefined label: unen-exc-notitle"
        in warnings(app)
    )
    assert (
        "_unenum_numref_notitle.rst:12: WARNING: undefined label: unen-exc-notitle"
        in warnings(app)
    )
    assert (
        "_unenum_numref_title.rst:4: WARNING: undefined label: unen-exc-label"
        in warnings(app)
    )
    assert (
        "_unenum_numref_title.rst:6: WARNING: undefined label: unen-exc-label"
        in warnings(app)
    )
    assert (
        "_unenum_numref_title.rst:8: WARNING: undefined label: unen-exc-label"
        in warnings(app)
    )
    assert (
        "_unenum_numref_title.rst:10: WARNING: undefined label: unen-exc-label"
        in warnings(app)
    )
    assert (
        "_unenum_numref_title.rst:12: WARNING: undefined label: unen-exc-label"
        in warnings(app)
    )


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
