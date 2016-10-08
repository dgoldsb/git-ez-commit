"""
Functions for finding differences between two versions of a Python code file

Terminology:
    current: The last (newest) version of the source
    previous: A previous version of the code
"""

import ast
import enum

DIFFERENCE_TREE_TYPES = [ast.ClassDef, ast.FunctionDef]

class ChangeType(enum.Enum):
    add = 1
    delete = 2
    change = 3


class DifferenceNode(object):
    """
    Helper to build a difference tree
    """
    def __init__(self, parent, value):
        self.parent = parent
        self.value = value
        self.children = []


class Difference(object):
    """
    The definition of a code difference
    """
    def __init__(self, change_type, previous_ast_node, current_ast_node):
        """
        :param change_type: The type of the difference, see ChangeType
        :param current_ast_node: The node in the current abstract syntax tree representing this change or None when not applicable
        :param previous_ast_node: The node in the previous abstract syntax tree representing this change or None when not applicable
        """
        self.type = change_type
        self.previous_ast_node = previous_ast_node
        self.current_ast_node = current_ast_node

    def test(self):
        pass


def find_ast_node(tree, node_name):
    pass


def generate_ast(source, filename):
    return ast.parse(source)


def search_nodes(tree_body, object_type):
    """
    Search for top-level nodes
    :param tree: The ast to search in
    :return: A tuple ([nodes_of_object_type], [code_not_of_object_type])
    """
    top_level = []
    # Consider everything not in a top level class to be in a single class
    not_object_type_code = []
    for node in tree_body:
        if type(node) is object_type:
            top_level.append(node)
        else:
            not_object_type_code.append(node)
    return top_level, not_object_type_code


def ast_differences(root, current_body, previous_body, root_types):
    added, current_code, deleted, previous_code, matching = \
        code_unit_changes(current_body, previous_body, root_types[0] if len(root_types)>0 else None)

    for n in deleted:
        diff = Difference(ChangeType.delete, n, None)
        diff_node = DifferenceNode(root, diff)
        root.children.append(diff_node)

    for n in added:
        diff = Difference(ChangeType.add, None, n)
        diff_node = DifferenceNode(root, diff)
        root.children.append(diff_node)

    children_have_difference = False

    popped_types = root_types[1:]

    for current_match, previous_match in matching:
        current_body = current_match.body if "body" in current_match._fields else []
        previous_body = previous_match.body if "body" in current_match._fields else []

        child_difference = expand_difference_tree(current_body, current_match, popped_types, previous_body,
                                                  previous_match, root)

        children_have_difference |= child_difference
    if len(current_code) > 0 or len(previous_code) > 0:
        child_difference = expand_difference_tree(current_code, current_code, popped_types, previous_code, previous_code, root)
        children_have_difference |= child_difference

    return children_have_difference or len(deleted) > 0 or len(added) > 0


def expand_difference_tree(current_body, current_match, types, previous_body, previous_match, root):
    diff = Difference(ChangeType.change, current_match, previous_match)
    diff_node = DifferenceNode(root, diff)
    child_difference = ast_differences(diff_node, current_body, previous_body, types)
    if child_difference:
        root.children.append(diff_node)
    return child_difference


def code_unit_changes(current_body, previous_body, node_type):
    if node_type is not None:
        current, current_code = search_nodes(current_body, node_type)
        previous, previous_code = search_nodes(previous_body, node_type)
    else:
        current = current_body
        current_code = []
        previous = previous_body
        previous_code = []
    current_dict = {c.name if type(c) is ast.FunctionDef or type(c) is ast.ClassDef else c.lineno: c for c in current}
    previous_dict = {c.name if type(c) is ast.FunctionDef or type(c) is ast.ClassDef else c.lineno: c for c in previous}
    current_set = set(current_dict.keys())
    previous_set = set(previous_dict.keys())
    matching = [(current_dict[name], previous_dict[name]) for name in current_set.intersection(previous_set)]
    deleted = [previous_dict[name] for name in previous_set.difference(current_set)]
    added = [current_dict[name] for name in current_set.difference(previous_set)]
    return added, current_code, deleted, previous_code, matching


def generate_differences(current, previous, filename):
    current_ast = generate_ast(current, filename)
    previous_ast = generate_ast(previous, filename)
    root = DifferenceNode(None, None)
    ast_differences(root, current_ast.body, previous_ast.body, DIFFERENCE_TREE_TYPES)
    return root
