from interpreter.expressions.expressions import CalculatedBufferItem
from interpreter.utils.generator_wapper import ReverseMessage, WaperName
from interpreter.var_const_concatinator.abstract import BufferItem
from syntax_analyzer.lexical.all_lexems import ALL_LEXICAL


class CaseController(object):

    def __init__(self):
        self.switch_stack = []
        self.case_stack = []
        self.switch_found = False
        self.case_found = False
        self.target_case_is_founded: list[bool] = []
        self.end_counter: list[int] = []
        self.case_controller: list[int] = []

    # def controller(self, lexeme: BufferItem) -> tuple[BufferItem, ReverseMessage | None]:
    #     if lexeme.result == ALL_LEXICAL.SWITCH:
    #         self.switch_found = True
    #         self.target_case_is_founded += [False]
    #         self.two_ends += [0]
    #     elif self.switch_found and isinstance(lexeme, CalculatedBufferItem):
    #         self.switch_stack += [lexeme.result]
    #         self.switch_found = False
    #
    #     if lexeme.result == ALL_LEXICAL.END:
    #         self.two_ends[0] += 1
    #     elif lexeme.result == ALL_LEXICAL.CASE:
    #         self.two_ends[0] = 0
    #
    #     if bool(self.two_ends) and self.two_ends[-1] == 2:
    #         self.two_ends.pop(-1)
    #         self.target_case_is_founded.pop(-1)
    #
    #
    #
    #     if lexeme.result == ALL_LEXICAL.CASE:
    #         self.case_found = True
    #     elif self.case_found and isinstance(lexeme, CalculatedBufferItem):
    #         # self.case_stack += [lexeme.result]
    #         self.case_found = False
    #         if lexeme.result == self.switch_stack[-1]:
    #             self.case_stack += [lexeme.result]
    #             self.target_case_is_founded[-1] = True
    #             return lexeme, None
    #         else:
    #             if self.target_case_is_founded[-1]:
    #                 return lexeme, ReverseMessage(
    #                     WaperName.syntax,
    #                     lambda i: i != ALL_LEXICAL.CASE and i != ALL_LEXICAL.END
    #                 )
    #             else:
    #                 return lexeme, ReverseMessage(WaperName.syntax, lambda i: i != ALL_LEXICAL.CASE)
    #
    #
    #     # if lexeme.result == ALL_LEXICAL.END:
    #     #     if len(self.switch_stack) == len(self.case_stack):
    #     #         if bool( self.case_stack):
    #     #             self.case_stack.pop(-1)
    #     #     else:
    #     #         if bool(self.switch_stack):
    #     #             self.switch_stack.pop(-1)
    #     #     pass
    #
    #
    #
    #
    #     return lexeme, None

    def controller(self, lexeme: BufferItem) -> tuple[BufferItem, ReverseMessage | None]:

        res_message = None

        if lexeme.result == ALL_LEXICAL.SWITCH:
            self.switch_found = True
            self.target_case_is_founded += [False]
            self.end_counter += [0]
            self.case_controller += [0]
        elif lexeme.result == ALL_LEXICAL.CASE:
            self.case_found = True
            self.end_counter[-1] = 0
            self.case_controller[-1] += 1

            if self.case_controller[-1] > 1:
                self.case_found = False
                res_message = ReverseMessage(
                    WaperName.syntax,
                    lambda i: i != ALL_LEXICAL.CASE and i != ALL_LEXICAL.END
                )
            else:
                pass

        elif lexeme.result == ALL_LEXICAL.END and bool(self.switch_stack):
            self.end_counter[-1] += 1
            # self.case_controller[-1] = 0

            if self.end_counter[-1] == 2:
                self.end_counter[-1] = 0
                if self.case_controller[-1] > 0:
                    res_message = ReverseMessage(
                        WaperName.syntax,
                        lambda i: i != ALL_LEXICAL.CASE and i != ALL_LEXICAL.END
                    )
                else:
                    self.switch_stack.pop(-1)
                    # self.case_stack.pop(-1)
                    self.end_counter.pop(-1)
                    self.case_controller.pop(-1)
                    self.target_case_is_founded.pop(-1)
            else:
                if self.case_controller[-1] == 1:
                    if len(self.case_stack) == len(self.switch_stack):
                        self.case_stack.pop(-1)
                self.case_controller[-1] -= 1



            # else:
            #     self.switch_stack.pop(-1)

        elif self.switch_found and isinstance(lexeme, CalculatedBufferItem):
            self.switch_found = False
            self.switch_stack += [lexeme.result]
        elif self.case_found and isinstance(lexeme, CalculatedBufferItem):
            self.case_found = False
            self.case_stack += [lexeme.result]
            if lexeme.result == self.switch_stack[-1]:
                self.target_case_is_founded[-1] = True
            # elif self.target_case_is_founded[-1] :
            #     res_message =
            else:
                res_message = ReverseMessage(
                                WaperName.syntax,
                                lambda i: i != ALL_LEXICAL.CASE and i != ALL_LEXICAL.END
                            )
        else:
            pass

        return lexeme, res_message