"""
Functions for finding differences between two versions of a Python code file

Terminology:
    current: The last (newest) version of the source
    previous: A previous version of the code
"""

import ast
import enum


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


def ast_differences(current_ast, previous_ast):
    root = DifferenceNode(None, None)

    current_classes, current_non_class_code = search_nodes(current_ast.body, ast.ClassDef)
    previous_classes, previous_non_class_code = search_nodes(previous_ast.body, ast.ClassDef)

    current_classes_dict = {c.name:c for c in current_classes}
    previous_classes_dict = {c.name:c for c in previous_classes}

    current_set = set(current_classes_dict.keys())
    previous_set = set(previous_classes_dict.keys())

    matching_classes = [current_classes_dict[name] for name in current_set.intersection(previous_set)]
    deleted_classes = [previous_classes_dict[name] for name in previous_set.difference(current_set)]
    added_classes = [current_classes_dict[name] for name in current_set.difference(previous_set)]


    class_differences = []
    for n in deleted_classes:
        class_differences.append(Difference(ChangeType.delete, n, None))

    for n in added_classes:
        class_differences.append(Difference(ChangeType.add, None, n))

    for diff in class_differences:
        node = DifferenceNode(root, diff)
        root.children.append(node)


    # Search for matching functions


    # Create list of differences

    return root


def generate_differences(current, previous, filename):
    current_ast = generate_ast(current, filename)
    previous_ast = generate_ast(previous, filename)
    return ast_differences(current_ast, previous_ast)


if __name__=="__main__":
    c = open("code_difference.py", "r")

    generate_differences(c.read(), "", "code_difference.py")

