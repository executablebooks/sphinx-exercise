import pytest
import shutil


@pytest.mark.sphinx("html", testroot="mybook")
def test_build(app):
    """Test building the book template and a few test configs."""
    app.build()
    assert (app.outdir / "index.html").exists()
    assert (app.outdir / "exercise").exists()
    assert (app.outdir / "solution").exists()


@pytest.mark.sphinx("html", testroot="mybook")
@pytest.mark.parametrize(
    "wmsg",
    [
        "_unenum_numref_mathtitle.rst:4: WARNING: undefined label: unen-exc-label-math",
        "_unenum_numref_mathtitle.rst:6: WARNING: undefined label: unen-exc-label-math",
        "_unenum_numref_mathtitle.rst:8: WARNING: undefined label: unen-exc-label-math",
        "_unenum_numref_mathtitle.rst:10: WARNING: undefined label: unen-exc-label-math",  # noqa: E501
        "_unenum_numref_notitle.rst:4: WARNING: undefined label: unen-exc-notitle",
        "_unenum_numref_notitle.rst:6: WARNING: undefined label: unen-exc-notitle",
        "_unenum_numref_notitle.rst:8: WARNING: undefined label: unen-exc-notitle",
        "_unenum_numref_notitle.rst:10: WARNING: undefined label: unen-exc-notitle",
        "_unenum_numref_title.rst:4: WARNING: undefined label: unen-exc-label",
        "_unenum_numref_title.rst:6: WARNING: undefined label: unen-exc-label",
        "_unenum_numref_title.rst:8: WARNING: undefined label: unen-exc-label",
        "_unenum_numref_title.rst:10: WARNING: undefined label: unen-exc-label",
        "_linked_ref_wronglabel.rst:5: WARNING: undefined label: foobar",
        "_linked_unenum_title.rst: WARNING: undefined label: wrong-ex-label",
        "_enum_duplicate_label.rst: WARNING: duplicate label: dup;",
        "_linked_duplicate_label.rst: WARNING: duplicate label: sol-duplicate-label;",
    ],
)
def test_warnings(app, warnings, wmsg):
    build_path = app.srcdir.joinpath("_build")
    shutil.rmtree(build_path)
    app.build()
    assert wmsg in warnings(app).replace("'", "")
