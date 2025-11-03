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
    "html", testroot="mybook", confoverrides={"style_solution_after_exercise": True}
)
def test_solution_no_link(app):
    """Test solution directive with style_solution_after_exercise=True removes hyperlink."""
    app.build()
    path_solution_directive = app.outdir / "solution" / "_linked_enum.html"
    assert path_solution_directive.exists()

    # get content markup
    soup = BeautifulSoup(
        path_solution_directive.read_text(encoding="utf8"), "html.parser"
    )

    sol = soup.select("div.solution")[0]
    title = sol.select("p.admonition-title")[0]

    # Check that there is NO hyperlink in the title when style_solution_after_exercise=True
    links = title.find_all("a")
    assert (
        len(links) == 0
    ), "Solution title should not contain hyperlink when style_solution_after_exercise=True"

    # Check that the title text still contains the exercise reference
    title_text = title.get_text()
    assert "Exercise" in title_text
    assert "This is a title" in title_text


@pytest.mark.sphinx(
    "html", testroot="mybook", confoverrides={"style_solution_after_exercise": False}
)
def test_solution_with_link(app):
    """Test solution directive with style_solution_after_exercise=False keeps hyperlink."""
    app.build()
    path_solution_directive = app.outdir / "solution" / "_linked_enum.html"
    assert path_solution_directive.exists()

    # get content markup
    soup = BeautifulSoup(
        path_solution_directive.read_text(encoding="utf8"), "html.parser"
    )

    sol = soup.select("div.solution")[0]
    title = sol.select("p.admonition-title")[0]

    # Check that there IS a hyperlink in the title when style_solution_after_exercise=False (default)
    links = title.find_all("a")
    assert (
        len(links) == 1
    ), "Solution title should contain hyperlink when style_solution_after_exercise=False"

    # Check that the link points to the exercise
    link = links[0]
    assert "href" in link.attrs
    assert "ex-number" in link["href"]


@pytest.mark.sphinx(
    "html", testroot="mybook", confoverrides={"style_solution_after_exercise": True}
)
def test_solution_no_link_unenum(app):
    """Test unnumbered solution directive with style_solution_after_exercise=True removes hyperlink."""
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
    ), "Solution title should not contain hyperlink when style_solution_after_exercise=True"

    # Check that the title text still contains the exercise reference
    title_text = title.get_text()
    assert "Exercise" in title_text
    assert "This is a title" in title_text
