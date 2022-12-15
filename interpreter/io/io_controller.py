from interpreter.expressions.expressions import CalculatedBufferItem
from interpreter.var_const_concatinator.abstract import BufferItem
from interpreter.var_const_concatinator.variables import VarBufferItem, VarActions
from syntax_analyzer.lexical.all_lexems import ALL_LEXICAL
from syntax_analyzer.lexical.terminals import OPTIONAL_BLANKS_ENUM
from syntax_analyzer.lexical import no_terminals


class VarController(object):
    def __init__(self):
        self.print_keyword_status = False
        self.input_keyword_status = False
        self.initing_var = None
        self.await_value = False

    def controller(self, current_item: BufferItem, variables_dict: dict):
        if current_item.result == ALL_LEXICAL.WRITE:
            self.print_keyword_status = True
        elif current_item.result == ALL_LEXICAL.READ:
            self.input_keyword_status = True

        if isinstance(current_item, VarBufferItem):
            if current_item.action == VarActions.define:
                if current_item.result in variables_dict:
                    raise SyntaxError("Переменная не может быть объявлена дважды")
                variables_dict[current_item.result] = None
            elif self.print_keyword_status:
                self.print_action(current_item, variables_dict)
                self.print_keyword_status = False
            elif self.input_keyword_status:
                variables_dict = self.input_action(current_item, variables_dict)
                self.input_keyword_status = False
        elif isinstance(current_item, CalculatedBufferItem):
            if self.print_keyword_status:
                self.print_action(current_item, variables_dict)
                self.print_keyword_status = False

        if self.initing_var is not None \
                and current_item.result not in list(OPTIONAL_BLANKS_ENUM) + [ALL_LEXICAL("=")] \
                and isinstance(current_item.result, no_terminals._first_NO_TERMINALS) is False \
                and isinstance(current_item, CalculatedBufferItem) is False:
            self.initing_var = None

        if isinstance(current_item, VarBufferItem):
            self.initing_var = current_item.result

        if current_item.result == ALL_LEXICAL("="):
            self.await_value = True
        elif self.await_value and isinstance(current_item, CalculatedBufferItem):
            if self.initing_var in variables_dict:
                variables_dict[self.initing_var] = current_item.result
            else:
                raise ValueError(f"Переменная {''.join([i.name for i in self.initing_var])} не определена")
            self.await_value = False
            self.initing_var = None
        return variables_dict

    @staticmethod
    def print_action(current_item: BufferItem, variables_dict: dict):

        if isinstance(current_item, CalculatedBufferItem):
            print('_' * 20)
            print(current_item.result)
            print('-' * 20)
        elif isinstance(current_item, VarBufferItem):
            if current_item.result in variables_dict:
                if variables_dict[current_item.result] is None:
                    raise SyntaxError("Переменная не была проинициализированна")

                print('_' * 20)
                print(variables_dict[current_item.result])
                print('-' * 20)
            else:
                print(variables_dict)
                print(current_item)
                raise SyntaxError("Переменная не была объявлена")
        else:
            raise ValueError()

    @staticmethod
    def input_action(current_item: BufferItem, variables_dict: dict):
        if current_item.result in variables_dict:
            variables_dict[current_item.result] = int(
                input(f"Введите значение для переменной "
                      f"{''.join([i.name for i in current_item.result])}:" + '\n')
            )
            # print(variables_dict[current_item.result])
        else:
            raise SyntaxError("Переменная не была объявлена")
        return variables_dict
