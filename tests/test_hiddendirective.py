from bs4 import BeautifulSoup
import pytest
import shutil


@pytest.mark.sphinx("html", testroot="hiddendirectives")
def test_warning(app, warnings):
    """Test warning thrown during the build"""
    build_path = app.srcdir.joinpath("_build")
    shutil.rmtree(build_path)
    app.build()

    assert (
        "_enum_hidden.rst: WARNING: duplicate label: ex-hidden-number;"
    ) in warnings(app)


@pytest.mark.sphinx("html", testroot="hiddendirectives")
@pytest.mark.parametrize(
    "idir",
    [
        "_enum_hidden.html",
        "_unenum_hidden.html",
    ],
)
def test_hidden_exercise(app, idir, file_regression):
    """Test exercise directive markup."""
    app.build()
    path_to_directive = app.outdir / idir
    assert path_to_directive.exists()

    # get content markup
    soup = BeautifulSoup(path_to_directive.read_text(encoding="utf8"), "html.parser")
    exercise = soup.select("div.exercise")
    assert len(exercise) == 0


@pytest.mark.sphinx("html", testroot="hiddendirectives")
@pytest.mark.parametrize(
    "idir",
    [
        "_linked_enum_hidden.html",
        "_linked_unenum_hidden.html",
    ],
)
def test_hidden_solution(app, idir, file_regression):
    """Test exercise directive markup."""
    app.build()
    path_to_directive = app.outdir / idir
    assert path_to_directive.exists()

    # get content markup
    soup = BeautifulSoup(path_to_directive.read_text(encoding="utf8"), "html.parser")
    solution = soup.select("div.solution")
    assert len(solution) == 0
