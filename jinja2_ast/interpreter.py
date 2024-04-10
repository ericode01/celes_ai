from typing import Any

from src.jinja2 import nodes
from collections import deque


class Interpreter:
    # def __init__(
    #     self,
    #     template: Template,
    #     context) -> None:
    #     self.template = template
    #     self.context = context
    #     self.updated_node_map = {}

    def execute(self, template: nodes.Template, context: dict):
        executioin_stack = deque()
        updated_node_map = {}

        # Add template first level nodes to execution stack
        executioin_stack.extend(template.body)
        executioin_stack.reverse()

        while len(executioin_stack) != 0:
            cur_node = executioin_stack.pop()
            f = self.get_visitor(cur_node)
            f(cur_node, context, executioin_stack, updated_node_map)

    def get_visitor(self, node: Node):
        """Return the visitor function for this node or `None` if no visitor
        exists for this node.  In that case the generic visit function is
        used instead.
        """
        return getattr(self, f"visit_{type(node).__name__}", None)

    def visit_assign(self, node: nodes.Assign, context, executioin_stack,
                     updated_node_map):

        right_side = node.node
        f = self.get_visitor(right_side)
        right_side_result = f(right_side, context)

        left_side = node.target
        f = self.get_visitor(left_side)
        f(left_side, right_side_result)

    def visit_for(self, node: nodes.For, context, executioin_stack: deque,
                  updated_node_map):
        right_side = node.iter
        f = self.get_visitor(right_side)
        right_side_result = f(right_side, context)

        index = node.cur_index
        if index >= len(right_side_result):
            return

        value = right_side_result[index]

        left_side = node.target
        f = self.get_visitor(left_side)
        f(left_side, value, context)

        node.cur_index += 1
        executioin_stack.append(node)

        for idx in range(len(node.body) - 1, -1, -1):
            executioin_stack.append(node.body[idx])

    def visit_name(self, node: nodes.Name, context: dict, value: Any = None):
        if node.ctx == 'load':
            if node.name in context:
                return context[node.name]
            else:
                raise Exception()

        if node.ctx == 'store':
            context[node.name] = value
            return

        raise Exception()

    def visit_if(self, node: nodes.If, context: dict, executioin_stack: deque):
        test = node.test
        f = self.get_visitor(test)
        test_result = f(test, context)

        if test_result:
            for idx in range(len(node.body) - 1, -1, -1):
                executioin_stack.append(node.body[idx])
            return

        if node.elif_:
            for elif_node in node.elif_:
                test = elif_node.test
                f = self.get_visitor(test)
                test_result = f(test, context)

                if test_result:
                    for idx in range(len(elif_node.body) - 1, -1, -1):
                        executioin_stack.append(elif_node.body[idx])
                    return

        if node.else_:
            else_node = node.else_
            for idx in range(len(else_node.body) - 1, -1, -1):
                executioin_stack.append(else_node.body[idx])

    def visit_and(self, node: nodes.And, context: dict):
        left_node = node.left
        left_f = self.get_visitor(left_node)
        left_result = left_f(left_node, context)

        right_node = node.right
        right_f = self.get_visitor(right_node)
        right_result = right_f(right_node, context)

        return left_result and right_result

    def visit_or(self, node: nodes.Or, context: dict):

        left_node = node.left
        left_f = self.get_visitor(left_node)
        left_result = left_f(left_node, context)

        right_node = node.right
        right_f = self.get_visitor(right_node)
        right_result = right_f(right_node, context)

        return left_result or right_result
