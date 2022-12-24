from bs4 import BeautifulSoup
import pytest

@pytest.mark.sphinx("html", testroot="otherlang")
def test_translation(app, file_regression):
    idir = "_exercice.html"
    app.build()
    path_exc_directive = app.outdir / "exercise" / idir
    soup = BeautifulSoup(path_exc_directive.read_text(encoding="utf8"), "html.parser")
    excs = soup.select("div.exercise")[0]
    file_regression.check(str(excs), basename=idir.split(".")[0], extension=".html")
