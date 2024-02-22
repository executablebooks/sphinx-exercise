import shutil
import pytest
import os
import packaging.version
import sphinx

from pathlib import Path

pytest_plugins = "sphinx.testing.fixtures"


if packaging.version.Version(sphinx.__version__) < packaging.version.Version("7.2.0"):
    @pytest.fixture
    def rootdir(tmpdir):
        from sphinx.testing.path import path
        src = path(__file__).parent.absolute() / "books"
        dst = tmpdir.join("books")
        shutil.copytree(src, dst)
        yield path(dst)
        shutil.rmtree(dst)
else:
    @pytest.fixture
    def rootdir(tmp_path):
        src = Path(__file__).parent.absolute() / "books"
        dst = tmp_path / "books"
        shutil.copytree(src, dst)
        yield dst
        shutil.rmtree(dst)


@pytest.fixture
def warnings():
    def read(app):
        return app._warning.getvalue().strip()

    return read


@pytest.fixture
def get_sphinx_app_doctree(file_regression):
    def read(
        app,
        docname="index",
        resolve=False,
        regress=False,
        flatten_outdir=False,
        sphinx_version=False,
    ):
        if resolve:
            doctree = app.env.get_and_resolve_doctree(docname, app.builder)
            extension = ".resolved.xml"
        else:
            doctree = app.env.get_doctree(docname)
            extension = ".xml"

        if sphinx_version:
            extension = sphinx_version + extension

        # convert absolute filenames
        findall = getattr(doctree, "findall", doctree.traverse)
        for node in findall(lambda n: "source" in n):
            node["source"] = Path(node["source"]).name

        if flatten_outdir:
            docname = docname.split("/")[-1]

        if regress:
            file_regression.check(
                doctree.pformat(), basename=docname, extension=extension
            )

        return doctree

    return read
