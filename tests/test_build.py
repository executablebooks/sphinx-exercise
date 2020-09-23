import pytest


@pytest.mark.sphinx("html", testroot="mybook")
def test_build(app):
    """Test building the book template and a few test configs."""
    app.build()
    assert (app.outdir / "index.html").exists()
    assert (app.outdir / "exercise").exists()
    assert (app.outdir / "solution").exists()
