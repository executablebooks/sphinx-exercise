# Support for LaTeX Markup


class LaTeXMarkup(object):

    CR = "\n"

    def visit_admonition(self):
        # latex_admonition_start
        return self.CR + "\\begin{sphinxadmonition}{note}"

    def depart_admonition(self):
        # latex_admonition_end
        return "\\end{sphinxadmonition}" + self.CR
