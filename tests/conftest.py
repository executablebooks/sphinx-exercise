import shutil
import pytest

from pathlib import Path
from sphinx.testing.path import path

pytest_plugins = "sphinx.testing.fixtures"


@pytest.fixture
def rootdir(tmpdir):
    src = path(__file__).parent.abspath() / "books"
    dst = tmpdir.join("books")
    shutil.copytree(src, dst)
    books = path(dst)
    yield books
    shutil.rmtree(dst)


@pytest.fixture
def warnings():
    def read(app):
        return app._warning.getvalue().strip()

    return read


@pytest.fixture
def get_sphinx_app_doctree(file_regression):
    def read(app, docname="index", resolve=False, regress=False, flatten_outdir=False):
        if resolve:
            doctree = app.env.get_and_resolve_doctree(docname, app.builder)
            extension = ".resolved.xml"
        else:
            doctree = app.env.get_doctree(docname)
            extension = ".xml"

        # convert absolute filenames
        for node in doctree.traverse(lambda n: "source" in n):
            node["source"] = Path(node["source"]).name

        if flatten_outdir:
            docname = docname.split("/")[-1]

        if regress:
            file_regression.check(
                doctree.pformat(), basename=docname, extension=extension
            )

        return doctree

    return read
