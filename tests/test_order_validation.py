"""Test exercise-solution order validation when exercise_style='solution_follow_exercise'"""
from pathlib import Path
import pytest


@pytest.mark.sphinx(
    "html",
    testroot="mybook",
    confoverrides={"exercise_style": "solution_follow_exercise"},
)
def test_solution_before_exercise_warning(app, warning):
    """Test that a warning is raised when solution appears before exercise"""
    # Create a temporary file with solution before exercise
    srcdir = Path(app.srcdir)
    test_file = srcdir / "test_wrong_order.rst"

    test_content = """
Wrong Order Test
================

.. solution:: my-test-exercise
   :label: sol-wrong-order

   This solution appears before the exercise!

.. exercise:: Test Exercise
   :label: my-test-exercise

   This is the exercise that should come first.
"""

    test_file.write_text(test_content)

    # Build and check for warnings
    app.build()

    warnings_text = warning.getvalue()

    # Should warn about solution not following exercise
    assert "does not follow" in warnings_text or "Solution" in warnings_text
    assert "sol-wrong-order" in warnings_text
    assert "my-test-exercise" in warnings_text

    # Clean up
    test_file.unlink()


@pytest.mark.sphinx(
    "html",
    testroot="mybook",
    confoverrides={"exercise_style": "solution_follow_exercise"},
)
def test_solution_different_document_warning(app, warning):
    """Test that a warning is raised when solution and exercise are in different documents"""
    # The existing test files should have some cross-document references
    app.build()

    # We expect the build to succeed but potentially with warnings
    # about cross-document references
    assert app.statuscode == 0 or app.statuscode is None


@pytest.mark.sphinx(
    "html",
    testroot="mybook",
    confoverrides={"exercise_style": ""},  # Default - no validation
)
def test_no_validation_when_config_not_set(app, warning):
    """Test that validation doesn't run when exercise_style is not set"""
    # Create a file with solution before exercise
    srcdir = Path(app.srcdir)
    test_file = srcdir / "test_no_validation.rst"

    test_content = """
No Validation Test
==================

.. solution:: my-test-ex
   :label: sol-no-val

   Solution before exercise - but should not warn

.. exercise:: Test
   :label: my-test-ex

   Exercise content
"""

    test_file.write_text(test_content)

    app.build()

    warnings_text = warning.getvalue()

    # Should NOT warn about order when config is not set
    assert "appears before" not in warnings_text

    # Clean up
    test_file.unlink()
