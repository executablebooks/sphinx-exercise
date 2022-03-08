from bs4 import BeautifulSoup
import pytest
import shutil


@pytest.mark.sphinx("html", testroot="gateddirective")
@pytest.mark.parametrize("docname", ["solution.html"])
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
@pytest.mark.parametrize("docname", ["solution"])
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
