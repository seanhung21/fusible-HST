import ete3


def basic_to_ete(basic_tree):
    return _basic_to_ete(basic_tree.root)


def _basic_to_ete(basic_node):
    ete_node = ete3.TreeNode()
    ete_node.add_feature('data', basic_node.data)
    for child in basic_node.children:
        ete_node.add_child(_basic_to_ete(child))
    return ete_node
