from sphinx.writers.latex import LaTeXTranslator
from docutils import nodes as docutil_nodes


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

    if node.tagname == parent_tag:
        return node.attributes["docname"]

    return None


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


def has_math_child(node):
    """ Check if a parent node as a math child node. """
    for item in node:
        if isinstance(item, docutil_nodes.math):
            return True
    return False


def get_refuri(node):
    """ Check both refuri and refid, to see which one is available. """
    id_ = ""
    if node.get("refuri", ""):
        id_ = node.get("refuri", "")

    if node.get("refid", ""):
        id_ = node.get("refid", "")

    return id_.split("#")[-1]
