from typing import Any

from interpreter.var_const_concatinator.abstract import BufferItem
from interpreter.var_const_concatinator.numbers import NumberBufferItem
from interpreter.var_const_concatinator.variables import VarBufferItem
from syntax_analyzer.lexical import no_terminals
from syntax_analyzer.lexical.all_lexems import ALL_LEXICAL
from syntax_analyzer.lexical.terminals import OPTIONAL_BLANKS_ENUM, CHARS_ENUM, NUMERALS_ENUM, BINARY_ENUM, \
    SPECIAL_CHARS_ENUM
from syntax_analyzer.main_syntax_analyzer import NO_TERMINALS

SC_ENUM = SPECIAL_CHARS_ENUM


class CalculatedBufferItem(BufferItem):
    def done(self):
        return super().done()
    def __repr__(self):
        return f"{self.__class__.__name__}({self.result})"


class ExprTreeList(object):
    def __init__(self, value, parent):
        self.value = value
        self.parent = parent

    def __repr__(self):
        return str(self.value)


class ExprTreeNode(object):
    def __init__(self, value, parent, left=None, right=None, priority=None):
        self.value = value
        self.parent = parent
        self.left = left
        self.right = right
        # if priority is None:
            # print("")
        self.priority = priority  # or (1 if value in [ALL_LEXICAL("/")] else 0)

    def __repr__(self):
        return str(self.value)


class ExpressionController(object):

    def __init__(self):
        self.expr_continue = False
        self.current_tree_stack: list[ExprTreeNode] | None = None
        self.bracket_nested = 0

    def expressions_tree_builder(self, lexeme: BufferItem, variables_dict):
        # print(lexeme)
        if lexeme.result == NO_TERMINALS.tE:
            yield lexeme
            self.expr_continue = True

        if self.expr_continue is True \
                and isinstance(lexeme.result, no_terminals._first_NO_TERMINALS) is False \
                and (
                isinstance(lexeme.result, (list, tuple)) is False

                and any(i == lexeme.result for i in
                        list(OPTIONAL_BLANKS_ENUM)
                        + list(BINARY_ENUM)
                        + [SC_ENUM("("), SC_ENUM(")")]) is False
                or (
                        isinstance(lexeme.result, (list, tuple))
                        and any(i == lexeme.result[0] for i in
                                list(CHARS_ENUM) + list(NUMERALS_ENUM)
                                ) is False
                )
        ):

            self.expr_continue = False
            if len(self.current_tree_stack) != 1:
                raise NotImplementedError()
            calculated_val = self.expression_calc(self.current_tree_stack[0], variables_dict)
            yield calculated_val
            self.current_tree_stack = None

        if self.expr_continue:
            # Формирование дерева
            if self.current_tree_stack is None:
                # создание первого элемента дерева
                self.current_tree_stack = [ExprTreeNode(None, None)]
                # raise NotImplementedError()

            if lexeme.result == ALL_LEXICAL("("):
                self.bracket_nested += 1
                self.current_tree_stack += [ExprTreeNode(None, None)]
            elif lexeme.result == ALL_LEXICAL(")"):
                self.bracket_nested -= 1
                paste_bracket_group = self.current_tree_stack.pop(-1)
                if self.current_tree_stack[-1].left is None:
                    self.current_tree_stack[-1].left = paste_bracket_group
                    paste_bracket_group.parent = self.current_tree_stack[-1]
                elif self.current_tree_stack[-1].right is None:
                    self.current_tree_stack[-1].right = paste_bracket_group
                    paste_bracket_group.parent = self.current_tree_stack[-1]
                elif isinstance(self.current_tree_stack[-1].right, ExprTreeNode) and \
                        self.current_tree_stack[-1].right.right is None:
                    self.current_tree_stack[-1].right.right = paste_bracket_group
                    paste_bracket_group.parent = self.current_tree_stack[-1].right

                else:
                    raise NotImplementedError()
            elif isinstance(lexeme.result, (list, tuple)):
                if self.current_tree_stack[-1].left is None:
                    self.current_tree_stack[-1].left = ExprTreeList(lexeme, self.current_tree_stack[-1])
                elif self.current_tree_stack[-1].right is None:
                    self.current_tree_stack[-1].right = ExprTreeList(lexeme, self.current_tree_stack[-1])
                else:
                    terminal_node = self.current_tree_stack[-1]
                    while terminal_node.right is not None:
                        terminal_node = terminal_node.right
                    terminal_node.right = ExprTreeList(lexeme, terminal_node)
            elif lexeme.result in [ALL_LEXICAL("+"), ALL_LEXICAL("-")]:
                if self.current_tree_stack[-1].left is None:
                    self.current_tree_stack[-1].left = ExprTreeList(
                        value=NumberBufferItem(
                            result=(ALL_LEXICAL("0"),), _done=True
                        ),
                        parent=self.current_tree_stack[-1].left
                    )
                    self.current_tree_stack[-1].value = lexeme
                    self.current_tree_stack[-1].priority = self.bracket_nested * 3 + 0
                elif self.current_tree_stack[-1].value is None:
                    self.current_tree_stack[-1].value = lexeme
                    self.current_tree_stack[-1].priority = self.bracket_nested * 3 + 0
                else:
                    if self.current_tree_stack[-1].priority == self.bracket_nested * 3 + 0:
                        new_left = self.current_tree_stack[-1]
                        new_parent: ExprTreeNode | None = self.current_tree_stack[-1].parent

                        new_left.parent = None
                        if new_parent is not None:
                            new_parent.right = None

                        new_current_node = ExprTreeNode(
                            lexeme,
                            new_parent,
                            left=new_left,
                            priority=self.bracket_nested * 3 + 0
                        )
                        self.current_tree_stack[-1] = new_current_node
                        new_left.parent = new_current_node
                        if new_parent is not None:
                            new_parent.right = new_current_node

                    elif self.current_tree_stack[-1].priority > self.bracket_nested * 3 + 0:
                        # new_parent = self.current_tree_stack[-1]
                        new_left = self.current_tree_stack[-1]

                        # if new_parent is not None:
                        #     new_parent.right = None
                        new_left.parent = None

                        new_current_item = ExprTreeNode(
                            lexeme,
                            None,
                            left=new_left,
                            priority=self.bracket_nested * 3 + 0
                        )

                        new_left.parent = new_current_item
                        self.current_tree_stack[-1] = new_current_item
                        # new_parent.right = new_current_item

                    else:
                        raise NotImplementedError()

            elif lexeme.result in [ALL_LEXICAL("/")]:
                if self.current_tree_stack[-1].value is None:
                    self.current_tree_stack[-1].value = lexeme
                    self.current_tree_stack[-1].priority = self.bracket_nested * 3 + 1
                else:
                    if self.current_tree_stack[-1].priority < self.bracket_nested * 3 + 1:
                        parent = self.current_tree_stack[-1]
                        new_left = self.current_tree_stack[-1].right

                        if parent is not None:
                            parent.right = None
                        new_left.parent = None

                        new_current_node = ExprTreeNode(
                            value=lexeme,
                            parent=parent,
                            left=new_left,
                            priority=self.bracket_nested * 3 + 1
                        )
                        new_left.parent = new_current_node
                        if parent is not None:
                            parent.right = new_current_node
                        # raise NotImplementedError()
                    elif self.current_tree_stack[-1].priority == self.bracket_nested * 3 + 1:
                        new_left = self.current_tree_stack[-1]
                        new_parent: ExprTreeNode | None = self.current_tree_stack[-1].parent

                        new_left.parent = None

                        if new_parent is not None:
                            new_parent.right = None

                        new_current_node = ExprTreeNode(
                            lexeme,
                            new_parent,
                            left=new_left,
                            priority=self.bracket_nested * 3 + 1
                        )
                        self.current_tree_stack[-1] = new_current_node
                        new_left.parent = new_current_node
                        if new_parent is not None:
                            new_parent.right = new_current_node


                    else:
                        raise NotImplementedError()
        else:
            yield lexeme


    @staticmethod
    def get_value_from_buffer_item(item: BufferItem, variables_dict: dict[VarBufferItem, Any]):
        if isinstance(item, VarBufferItem):
            return variables_dict[item.result]
        elif isinstance(item, NumberBufferItem):
            return int("".join([i.name for i in item.result]))
        elif isinstance(item, CalculatedBufferItem):
            return item.result
        else:
            raise NotImplementedError()
    @classmethod
    def expression_calc(
            cls,
            expr_tree: ExprTreeNode,
            variables_dict: dict[VarBufferItem, Any]
    ):
        current_node = expr_tree
        while True:
            if isinstance(current_node, ExprTreeNode) \
                    and current_node.left is not None:
                current_node = current_node.left
            elif isinstance(current_node, ExprTreeList):
                if isinstance(current_node.parent.right, ExprTreeList):
                    # Вычислить значения
                    left = cls.get_value_from_buffer_item(current_node.value, variables_dict)
                    right = cls.get_value_from_buffer_item(current_node.parent.right.value, variables_dict)
                    if current_node.parent.value.result == ALL_LEXICAL("+"):
                        new_val = left + right
                    elif current_node.parent.value.result == ALL_LEXICAL("-"):
                        new_val = left - right
                    elif current_node.parent.value.result == ALL_LEXICAL("/"):
                        new_val = left // right
                    else:
                        # print(current_node.parent.value)
                        raise NotImplementedError()
                    grand_parent = current_node.parent.parent
                    new_tree_list = ExprTreeList(
                        value=(new_calc_buff_item := CalculatedBufferItem(result=new_val)),
                        parent=grand_parent
                    )
                    if grand_parent is None:
                        return new_calc_buff_item
                    if grand_parent.left == current_node.parent:
                        grand_parent.left = new_tree_list
                    else:
                        grand_parent.right = new_tree_list

                    current_node = grand_parent
                elif current_node.parent.right is None:
                    raise NotImplementedError()
                else:
                    current_node = current_node.parent.right
            else:
                break
        # return 0