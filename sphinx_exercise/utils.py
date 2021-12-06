# Utility functions

from sphinx.writers.latex import LaTeXTranslator


def find_parent(env, node, parent_tag):
    """Find the nearest parent node with the given tagname."""

    while True:
        node = node.parent
        if node is None:
            return None
        # parent should be a document in toc
        if (
            "docname" in node.attributes
            and env.titles[node.attributes["docname"]].astext().lower()
            in node.attributes["names"]
        ):
            return node.attributes["docname"]


def get_node_number(self, node, typ) -> str:
    """Get the number for the directive node for HTML."""

    ids = node.attributes.get("ids", [])[0]
    if isinstance(self, LaTeXTranslator):
        docname = find_parent(self.builder.env, node, "section")
    else:
        docname = node.attributes.get("docname", "")
        # Latex does not have builder.fignumbers
    fignumbers = self.builder.env.toc_fignumbers.get(docname, {})
    number = fignumbers.get(typ, {}).get(ids, ())
    return ".".join(map(str, number))
