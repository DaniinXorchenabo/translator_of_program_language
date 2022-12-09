from dataclasses import dataclass
from typing import Any

from interpreter.var_const_concatinator.abstract import BufferItem
from syntax_analyzer.lexical import no_terminals
from syntax_analyzer.lexical.all_lexems import ALL_LEXICAL
from syntax_analyzer.lexical.terminals import NUMERALS_ENUM


@dataclass
class NumberBufferItem(BufferItem):
    _done: bool = False

    def done(self):
        return self._done


class NumController(object):
    def __init__(self):
        self.current_num = None

    def concatenate(
            self,
            grammar_buffer: list[ALL_LEXICAL],
            current_item: ALL_LEXICAL,
    ):
        # print(current_item)
        if any(current_item.name == i.name for i in NUMERALS_ENUM):
            # if bool(grammar_buffer) \
            #         and isinstance(grammar_buffer[-1].result, (list, tuple)) \
            #         and any(grammar_buffer[-1].result[0].name == i.name for i in NUMERALS_ENUM):
            if self.current_num is not None:
                self.current_num.result = (*self.current_num.result, current_item)
            else:
                grammar_buffer += [NumberBufferItem(result = (current_item,))]
                self.current_num = grammar_buffer[-1]
            return grammar_buffer
        elif isinstance(current_item, no_terminals._first_NO_TERMINALS):
            return grammar_buffer
        else:
            # if bool(grammar_buffer) \
            #         and isinstance(grammar_buffer[-1].result, (list, tuple)) \
            #         and  any(grammar_buffer[-1].result[0].name == i.name for i in NUMERALS_ENUM):
            if self.current_num is not None:
                # Окончание цифровой цепочки
                self.current_num._done = True
                self.current_num = None
            return grammar_buffer
