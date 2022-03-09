import os
import pytest
import shutil
from bs4 import BeautifulSoup
from sphinx.errors import ExtensionError

from sphinx.testing.util import strip_escseq


@pytest.mark.sphinx("html", testroot="gateddirective")
@pytest.mark.parametrize("docname", ["exercise-gated.html"])
def test_gated_exercise_build(app, docname, file_regression):
    app.build()
    path_to_html = app.outdir / docname
    # get content markup
    soup = BeautifulSoup(path_to_html.read_text(encoding="utf8"), "html.parser")
    exercise_directives = soup.select("div.exercise")
    for idx, ed in enumerate(exercise_directives):
        basename = docname.split(".")[0] + f"-{idx}"
        file_regression.check(str(ed), basename=basename, extension=".html")


@pytest.mark.sphinx("html", testroot="gateddirective")
@pytest.mark.parametrize("docname", ["exercise-gated"])
def test_gated_exercise_doctree(app, docname, get_sphinx_app_doctree):
    # Clean Up Build Directory from Previous Runs
    build_dir = "/".join(app.outdir.split("/")[:-1])
    shutil.rmtree(build_dir)
    # Test
    app.build()
    get_sphinx_app_doctree(
        app,
        docname,
        resolve=False,
        regress=True,
    )


@pytest.mark.sphinx("html", testroot="gateddirective")
@pytest.mark.parametrize(
    "docname", ["solution-exercise.html", "solution-exercise-gated.html"]
)
def test_gated_solution_build(app, docname, file_regression):
    app.build()
    path_to_html = app.outdir / docname
    # get content markup
    soup = BeautifulSoup(path_to_html.read_text(encoding="utf8"), "html.parser")
    solution_directives = soup.select("div.solution")
    for idx, sd in enumerate(solution_directives):
        basename = docname.split(".")[0] + f"-{idx}"
        file_regression.check(str(sd), basename=basename, extension=".html")


@pytest.mark.sphinx("html", testroot="gateddirective")
@pytest.mark.parametrize("docname", ["solution-exercise", "solution-exercise-gated"])
def test_gated_solution_doctree(app, docname, get_sphinx_app_doctree):
    # Clean Up Build Directory from Previous Runs
    build_dir = "/".join(app.outdir.split("/")[:-1])
    shutil.rmtree(build_dir)
    # Test
    app.build()
    get_sphinx_app_doctree(
        app,
        docname,
        resolve=False,
        regress=True,
    )


# Errors


def getwarning(warnings):
    return strip_escseq(warnings.getvalue().replace(os.sep, "/"))


@pytest.mark.sphinx("html", testroot="gateddirective")
def test_gated_solution_errors_1(app, warning):
    app.config.exclude_patterns = ["build", "_build", "solution_errors_[2,3]*"]
    try:
        app.build()
    except ExtensionError:
        warnings = getwarning(warning)
        warn1 = "is missing a solution-end directive"
        warn2 = "solution-start at line: 20"
        for warn in [warn1, warn2]:
            assert warn in warnings
        assert True
    else:
        assert False


@pytest.mark.sphinx("html", testroot="gateddirective")
def test_gated_solution_errors_2(app, warning):
    app.config.exclude_patterns = ["build", "_build", "solution_errors_[1,3]*"]
    try:
        app.build()
    except ExtensionError:
        warnings = getwarning(warning)
        warn1 = "is missing a solution-start directive"
        warn2 = "solution-end at line: 54"
        for warn in [warn1, warn2]:
            assert warn in warnings
        assert True
    else:
        assert False


@pytest.mark.sphinx("html", testroot="gateddirective")
def test_gated_solution_errors_3(app, warning):
    app.config.exclude_patterns = ["build", "_build", "solution_errors_[1,2]*"]
    try:
        app.build()
    except ExtensionError:
        warnings = getwarning(warning)
        warn1 = "contains nested solution-start and solution-end directives"
        warn2 = "solution-start at line: 16\n  solution-start at line: 19\n  solution-end at line: 22\n  solution-end at line: 25"  # noqa: #501
        for warn in [warn1, warn2]:
            assert warn in warnings
        assert True
    else:
        assert False
