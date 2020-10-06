from bs4 import BeautifulSoup
import pytest


@pytest.mark.sphinx("html", testroot="mybook")
@pytest.mark.parametrize(
    "idir",
    [
        "_linked_enum.html",
        "_linked_enum_class.html",
        "_linked_unenum_mathtitle.html",
        "_linked_unenum_mathtitle2.html",
        "_linked_unenum_notitle.html",
        "_linked_unenum_title.html",
        "_linked_wrong_targetlabel.html",
    ],
)
def test_solution(app, idir, file_regression):
    """Test solution directive markup."""
    app.build()
    path_solution_directive = app.outdir / "solution" / idir
    assert path_solution_directive.exists()

    # get content markup
    soup = BeautifulSoup(
        path_solution_directive.read_text(encoding="utf8"), "html.parser"
    )

    sol = soup.select("div.solution")[0]
    file_regression.check(str(sol), basename=idir.split(".")[0], extension=".html")


@pytest.mark.sphinx("html", testroot="mybook")
@pytest.mark.parametrize(
    "idir",
    [
        "_linked_ref_enum.html",
        "_linked_ref_unenum_mathtitle.html",
        "_linked_ref_unenum_mathtitle2.html",
        "_linked_ref_unenum_notitle.html",
        "_linked_ref_unenum_title.html",
    ],
)
def test_reference(app, idir, file_regression):
    """Test solution ref role markup."""
    app.builder.build_all()
    path_solution_directive = app.outdir / "solution" / idir
    assert path_solution_directive.exists()
    # get content markup
    soup = BeautifulSoup(
        path_solution_directive.read_text(encoding="utf8"), "html.parser"
    )

    excs = ""
    all_refs = soup.select("p")
    for ref in all_refs:
        excs += f"{ref}\n"

    file_regression.check(
        str(excs[:-1]), basename=idir.split(".")[0], extension=".html"
    )
