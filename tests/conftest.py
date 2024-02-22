import shutil
import pytest
import packaging.version
import sphinx
import re

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


# comparison files will need updating
# alternatively the resolution of https://github.com/ESSS/pytest-regressions/issues/32
@pytest.fixture()
def file_regression(file_regression):
    return FileRegression(file_regression)


class FileRegression:
    ignores = (
        # TODO: Remove when support for Sphinx<=6 is dropped,
        re.escape(" translation_progress=\"{'total': 0, 'translated': 0}\""),
        # TODO: Remove when support for Sphinx<7.2 is dropped,
        r"original_uri=\"[^\"]*\"\s",
    )

    def __init__(self, file_regression):
        self.file_regression = file_regression

    def check(self, data, **kwargs):
        return self.file_regression.check(self._strip_ignores(data), **kwargs)

    def _strip_ignores(self, data):
        for ig in self.ignores:
            data = re.sub(ig, "", data)
        return data
