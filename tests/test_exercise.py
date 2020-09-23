from bs4 import BeautifulSoup
import pytest


@pytest.mark.sphinx("html", testroot="mybook")
@pytest.mark.parametrize(
    "idir",
    [
        "_exercise_labeled_titled_with_classname.html",
        "_exercise_nonumber.html",
        "_exercise_title_with_inline_math.html",
        "_exercise_unlabeled_math.html",
        "_exercise_with_labeled_math.html",
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


# @pytest.mark.sphinx("html", testroot="mybook")
# @pytest.mark.parametrize(
#     "idir", ["_exercise_numbered_reference.html", "_exercise_text_reference.html"]
# )
# def test_reference(app, idir, file_regression):
#     """Test exercise ref role markup."""
#     app.builder.build_all()
#     path_exc_directive = app.outdir / "exercise" / idir
#     assert path_exc_directive.exists()
#     # get content markup
#     soup = BeautifulSoup(path_exc_directive.read_text(encoding="utf8"), "html.parser")

#     excs = soup.select("p")[0]
#     file_regression.check(str(excs), basename=idir.split(".")[0], extension=".html")
