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
    # assert "WARNING: invalid numfig_format: some text {name}" in warnings(app)
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
    assert "_linked_ref_wronglabel.rst:5: WARNING: undefined label: foobar" in warnings(
        app
    )
    assert (
        "_linked_unenum_title.rst: WARNING: undefined label: wrong-ex-label"
        in warnings(app)
    )
    assert "_enum_duplicate_label.rst: WARNING: duplicate label: dup;" in warnings(app)
    assert (
        "_linked_duplicate_label.rst: WARNING: duplicate label: sol-duplicate-label;"
        in warnings(app)
    )
