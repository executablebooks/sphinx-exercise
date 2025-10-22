import os
import pytest
import re
import shutil
import sphinx
from bs4 import BeautifulSoup
from sphinx.errors import ExtensionError
from pathlib import Path

# strip_escape_sequences was removed in Sphinx 7
try:
    from sphinx.util.console import strip_escape_sequences as strip_escseq
except ImportError:
    # Fallback for Sphinx 7+: simple ANSI escape sequence stripper
    def strip_escseq(text: str) -> str:
        """Remove ANSI escape sequences from text."""
        return re.sub(r"\x1b\[[0-9;]*m", "", text)


# Sphinx 8.1.x (Python 3.10 only) has different XML output than 8.2+
# Use .sphinx8.1 for 8.1.x, .sphinx8 for 8.2+ (the standard)
if sphinx.version_info[0] == 8 and sphinx.version_info[1] == 1:
    SPHINX_VERSION = f".sphinx{sphinx.version_info[0]}.{sphinx.version_info[1]}"
else:
    SPHINX_VERSION = f".sphinx{sphinx.version_info[0]}"


@pytest.mark.sphinx("html", testroot="gateddirective")
@pytest.mark.parametrize("docname", ["exercise-gated.html"])
def test_gated_exercise_build(app, docname, file_regression):
    app.build()
    path_to_html = Path(app.outdir) / docname
    # get content markup
    soup = BeautifulSoup(path_to_html.read_text(encoding="utf8"), "html.parser")
    exercise_directives = soup.select("div.exercise")
    for idx, ed in enumerate(exercise_directives):
        basename = docname.split(".")[0] + f"-{idx}"
        file_regression.check(
            str(ed), basename=basename, extension=f"{SPHINX_VERSION}.html"
        )


@pytest.mark.sphinx("html", testroot="gateddirective")
@pytest.mark.parametrize("docname", ["exercise-gated"])
def test_gated_exercise_doctree(app, docname, get_sphinx_app_doctree):
    # Clean Up Build Directory from Previous Runs
    shutil.rmtree(str(app.outdir))
    # Test
    app.build()
    get_sphinx_app_doctree(
        app,
        docname,
        resolve=False,
        regress=True,
        sphinx_version=SPHINX_VERSION,
    )


@pytest.mark.sphinx("html", testroot="gateddirective")
@pytest.mark.parametrize(
    "docname", ["solution-exercise.html", "solution-exercise-gated.html"]
)
def test_gated_solution_build(app, docname, file_regression):
    app.build()
    path_to_html = Path(app.outdir) / docname
    # get content markup
    soup = BeautifulSoup(path_to_html.read_text(encoding="utf8"), "html.parser")
    solution_directives = soup.select("div.solution")
    for idx, sd in enumerate(solution_directives):
        basename = docname.split(".")[0] + f"-{idx}"
        file_regression.check(
            str(sd), basename=basename, extension=f"{SPHINX_VERSION}.html"
        )


@pytest.mark.sphinx("html", testroot="gateddirective")
@pytest.mark.parametrize("docname", ["solution-exercise", "solution-exercise-gated"])
def test_gated_solution_doctree(app, docname, get_sphinx_app_doctree):
    # Clean Up Build Directory from Previous Runs
    shutil.rmtree(str(app.outdir))
    # Test
    app.build()
    get_sphinx_app_doctree(
        app, docname, resolve=False, regress=True, sphinx_version=SPHINX_VERSION
    )


# Errors


def getwarning(warnings):
    return strip_escseq(warnings.getvalue().replace(os.sep, "/"))


@pytest.mark.sphinx("html", testroot="gateddirective")
def test_gated_exercise_errors_1(app, warning):
    app.config.exclude_patterns = [
        "build",
        "_build",
        "solution_errors_[1,2,3]*",
        "exercise_errors_[2,3]*",
    ]
    try:
        app.build()
    except ExtensionError:
        warnings = getwarning(warning)
        warn1 = "is missing a exercise-end directive"
        warn2 = "exercise-start at line: 20"
        for warn in [warn1, warn2]:
            assert warn in warnings
        assert True
    else:
        assert False


@pytest.mark.sphinx("html", testroot="gateddirective")
def test_gated_exercise_errors_2(app, warning):
    app.config.exclude_patterns = [
        "build",
        "_build",
        "solution_errors_[1,2,3]*",
        "exercise_errors_[1,3]*",
    ]
    try:
        app.build()
    except ExtensionError:
        warnings = getwarning(warning)
        warn1 = "is missing a exercise-start directive"
        warn2 = "exercise-end at line: 23"
        for warn in [warn1, warn2]:
            assert warn in warnings
        assert True
    else:
        assert False


@pytest.mark.sphinx("html", testroot="gateddirective")
def test_gated_exercise_errors_3(app, warning):
    app.config.exclude_patterns = [
        "build",
        "_build",
        "solution_errors_[1,2,3]*",
        "exercise_errors_[1,2]*",
    ]
    try:
        app.build()
    except ExtensionError:
        warnings = getwarning(warning)
        warn1 = "contains nested exercise-start and exercise-end directives"
        warn2 = "exercise-start at line: 16\n  exercise-start at line: 19\n  exercise-end at line: 22\n  exercise-end at line: 25"  # noqa: #501
        for warn in [warn1, warn2]:
            assert warn in warnings
        assert True
    else:
        assert False


@pytest.mark.sphinx("html", testroot="gateddirective")
def test_gated_solution_errors_1(app, warning):
    app.config.exclude_patterns = [
        "build",
        "_build",
        "exercise_errors_[1,2,3]*",
        "solution_errors_[2,3]*",
    ]
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
    app.config.exclude_patterns = [
        "build",
        "_build",
        "exercise_errors_[1,2,3]*",
        "solution_errors_[1,3]*",
    ]
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
    app.config.exclude_patterns = [
        "build",
        "_build",
        "exercise_errors_[1,2,3]*",
        "solution_errors_[1,2]*",
    ]
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
