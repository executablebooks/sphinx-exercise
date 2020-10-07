import pytest
import shutil


@pytest.mark.sphinx("html", testroot="duplicatelabel")
def test_duplicates(app, warnings):
    build_path = app.srcdir.joinpath("_build")
    shutil.rmtree(build_path)
    app.build()

    assert "WARNING: duplicate label: label-1;" in warnings(app)
    assert "WARNING: duplicate label: label-2;" in warnings(app)
