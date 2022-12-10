import enum
from dataclasses import dataclass
from typing import Any

from interpreter.var_const_concatinator.abstract import BufferItem
from syntax_analyzer.lexical import no_terminals
from syntax_analyzer.lexical.all_lexems import ALL_LEXICAL
from syntax_analyzer.lexical.terminals import CHARS_ENUM, OPTIONAL_BLANKS_ENUM


class VarActions(enum.Enum):
    define = 'define'
    read = 'read'
    write = 'write'


@dataclass
class ResultStructure:
    match: bool
    match_end: bool | None
    result_buffer: list[Any] | None
    var_action_stack: list[Any] | None = None

    def __iter__(self):
        return iter([self.match, self.match_end, self.result_buffer, self.var_action_stack])


@dataclass
class VarBufferItem(BufferItem):
    action: VarActions | None = None

    def done(self):
        return self.action is not None

    def __repr__(self):
        return super().__repr__()


@dataclass
class ResultVarActionStructure:
    match: bool
    result: VarActions | None
    stack: list[Any] | None

    def __iter__(self):
        return iter([self.match, self.result, self.stack])


Var = tuple[ALL_LEXICAL, ...]
VarActionType = tuple[Var, VarActions]


class VariablesController(object):
    def __init__(self):
        self.const_var_status = None
        self.current_var = None

    def builder(self, grammar_buffer, current_item, var_action_stack):
        var_res, var_end, new_grammar_buf, new_var_action_stack = self._builder(
            grammar_buffer, current_item, var_action_stack
        )
        if new_grammar_buf is not None:
            grammar_buffer = new_grammar_buf
        if var_end:
            var_action_stack = new_var_action_stack
            # self.current_var = None
        return grammar_buffer, var_action_stack

    def _builder(
            self,
            grammar_buffer: list[ALL_LEXICAL],
            current_item: ALL_LEXICAL,
            var_action_stack
    ):
        # print(current_item)
        if any(current_item.name == i.name for i in CHARS_ENUM):
            # if bool(grammar_buffer) \
            #         and isinstance(grammar_buffer[-1].result, (list, tuple)) \
            #         and any(grammar_buffer[-1].result[0].name == i.name for i in CHARS_ENUM):
            if self.current_var is not None:
                self.current_var.result = (*self.current_var.result, current_item)
            else:
                grammar_buffer += [VarBufferItem(result=(current_item,))]
                self.current_var = grammar_buffer[-1]
            return ResultStructure(True, False, grammar_buffer, None)

        # if bool(grammar_buffer) \
        #         and isinstance(grammar_buffer[-1].result, (list, tuple)) \
        #         and any(grammar_buffer[-1].result[0].name == i.name for i in CHARS_ENUM) \
        #         and isinstance(current_item, no_terminals._first_NO_TERMINALS) is False:
        if isinstance(current_item, no_terminals._first_NO_TERMINALS):
            return ResultStructure(False, None, None, None)
        if self.current_var is not None:
            var_action_stack += [self.current_var]
            self.current_var = None
            return ResultStructure(False, True, None, var_action_stack)

        return ResultStructure(False, None, None, None)

    def action_identifier(self, var_action_stack, lexeme):
        var_ac_res, var_action, new_var_action_stack = self._action_identifier(var_action_stack, lexeme)
        if new_var_action_stack is not None:
            var_action_stack = new_var_action_stack
        return var_action_stack

    def _action_identifier(
            self,
            var_action_stack: list[VarBufferItem],
            current_item: ALL_LEXICAL,
    ):

        if current_item == ALL_LEXICAL.VAR:
            self.const_var_status = VarActions.define
        elif current_item == ALL_LEXICAL.INTEGER:
            self.const_var_status = None

        if bool(var_action_stack) and var_action_stack[-1].action is None:
            if current_item.name == ALL_LEXICAL("=").name:
                if bool(var_action_stack) and var_action_stack[-1].action is None:
                    var_action_stack[-1].action = VarActions.write
                    return ResultVarActionStructure(True, VarActions.write, var_action_stack)
                else:
                    return ResultVarActionStructure(False, None, None)

            elif self.const_var_status is not None:
                if bool(var_action_stack) and var_action_stack[-1].action is None:
                    var_action_stack[-1].action = self.const_var_status
                    return ResultVarActionStructure(True, self.const_var_status, var_action_stack)
                else:
                    return ResultVarActionStructure(False, None, None)

            elif isinstance(current_item, no_terminals._first_NO_TERMINALS) is False \
                    and any(current_item.name == i.name for i in
                            list(OPTIONAL_BLANKS_ENUM) + [ALL_LEXICAL("=")]
                            ) is False:
                if bool(var_action_stack) and var_action_stack[-1].action is None:
                    var_action_stack[-1].action = VarActions.read
                    return ResultVarActionStructure(True, VarActions.read, var_action_stack)
                else:
                    return ResultVarActionStructure(False, None, None)

        return ResultVarActionStructure(False, None, None)


