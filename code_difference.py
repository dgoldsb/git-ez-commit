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


class Difference(object):
    def __init__(self, change_type, previous_ast_node, current_ast_node):
        """
        The definition of a code difference
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


def ast_differences(current_ast, previous_ast):
    pass


def generate_differences(current, previous, filename):
    current_ast = generate_ast(current, filename)
    previous_ast = generate_ast(previous, filename)
    return ast_differences(current_ast, previous_ast)


if __name__=="__main__":
    c = open("code_difference.py", "r")

    generate_differences(c.read(), "", "code_difference.py")

