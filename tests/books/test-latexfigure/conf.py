# Test root for captioned figures inside exercise and solution boxes in
# LaTeX output (https://github.com/executablebooks/sphinx-exercise/issues/94)

project = "sphinx-exercise Test"
copyright = "2020, QuantEcon Developers"
author = "QuantEcon Developers"

extensions = ["sphinx_exercise", "myst_nb"]

# notebook.ipynb stores its outputs, so the test does not need a kernel
nb_execution_mode = "off"
