from bs4 import BeautifulSoup
import pytest
import sphinx

# Sphinx 8.1.x (Python 3.10 only) has different XML output than 8.2+
# Use .sphinx8.1 for 8.1.x, .sphinx8 for 8.2+ (the standard)
if sphinx.version_info[0] == 8 and sphinx.version_info[1] == 1:
    SPHINX_VERSION = f".sphinx{sphinx.version_info[0]}.{sphinx.version_info[1]}"
else:
    SPHINX_VERSION = f".sphinx{sphinx.version_info[0]}"


@pytest.mark.sphinx(
    "html",
    testroot="mybook",
    confoverrides={"exercise_style": "solution_follow_exercise"},
)
def test_solution_no_link(app):
    """Test solution directive with exercise_style='solution_follow_exercise' removes hyperlink."""
    app.build()
    path_solution_directive = app.outdir / "solution" / "_linked_enum.html"
    assert path_solution_directive.exists()

    # get content markup
    soup = BeautifulSoup(
        path_solution_directive.read_text(encoding="utf8"), "html.parser"
    )

    sol = soup.select("div.solution")[0]
    title = sol.select("p.admonition-title")[0]

    # Check that there is NO hyperlink in the title when exercise_style='solution_follow_exercise'
    links = title.find_all("a")
    assert (
        len(links) == 0
    ), "Solution title should not contain hyperlink when exercise_style='solution_follow_exercise'"

    # Check that the title is just "Solution" without exercise reference
    title_text = title.get_text()
    assert (
        title_text.strip() == "Solution"
    ), "Solution title should be just 'Solution' when exercise_style='solution_follow_exercise'"


@pytest.mark.sphinx("html", testroot="mybook", confoverrides={"exercise_style": ""})
def test_solution_with_link(app):
    """Test solution directive with exercise_style='' (default) keeps hyperlink."""
    app.build()
    path_solution_directive = app.outdir / "solution" / "_linked_enum.html"
    assert path_solution_directive.exists()

    # get content markup
    soup = BeautifulSoup(
        path_solution_directive.read_text(encoding="utf8"), "html.parser"
    )

    sol = soup.select("div.solution")[0]
    title = sol.select("p.admonition-title")[0]

    # Check that there IS a hyperlink in the title when exercise_style='' (default)
    links = title.find_all("a")
    assert (
        len(links) == 1
    ), "Solution title should contain hyperlink when exercise_style='' (default)"

    # Check that the link points to the exercise
    link = links[0]
    assert "href" in link.attrs
    assert "ex-number" in link["href"]


@pytest.mark.sphinx(
    "html",
    testroot="mybook",
    confoverrides={"exercise_style": "solution_follow_exercise"},
)
def test_solution_no_link_unenum(app):
    """Test unnumbered solution directive with exercise_style='solution_follow_exercise' removes hyperlink."""
    app.build()
    path_solution_directive = app.outdir / "solution" / "_linked_unenum_title.html"
    assert path_solution_directive.exists()

    # get content markup
    soup = BeautifulSoup(
        path_solution_directive.read_text(encoding="utf8"), "html.parser"
    )

    sol = soup.select("div.solution")[0]
    title = sol.select("p.admonition-title")[0]

    # Check that there is NO hyperlink in the title
    links = title.find_all("a")
    assert (
        len(links) == 0
    ), "Solution title should not contain hyperlink when exercise_style='solution_follow_exercise'"

    # Check that the title is just "Solution" without exercise reference
    title_text = title.get_text()
    assert (
        title_text.strip() == "Solution"
    ), "Solution title should be just 'Solution' when exercise_style='solution_follow_exercise'"
