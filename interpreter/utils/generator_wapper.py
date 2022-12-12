import enum
from dataclasses import dataclass
from itertools import takewhile, dropwhile
from typing import Callable, Any, Generator, Iterator


class WaperName(enum.Enum):
    syntax = 'syntax'
    v_c_concatenate = 'v_c_concatenate'
    expr_calc = 'expr_calc'
    var_controller = 'var_controller'
    switch_case = 'switch_case'


@dataclass
class ReverseMessage(object):
    to_waper: WaperName
    filter_func: Callable[[Any, ...], Any] | None = None


def reverse_gen_waper(inp_gen: Generator | Iterator, waper_name: WaperName):
    while True:
        try:
            if hasattr(inp_gen, 'send'):
                item = next(inp_gen)
            else:
                item = next(inp_gen)
            reverse_msg = item
            while reverse_msg is not None:
                reverse_msg = yield item
                if isinstance( reverse_msg, ReverseMessage) :
                    # print(waper_name, reverse_msg, )
                    if reverse_msg.to_waper == waper_name:
                        if reverse_msg.filter_func is not None:
                            inp_gen = dropwhile(reverse_msg.filter_func, inp_gen)
                            # yield next(inp_gen)
                            # reverse_msg = yield item
                    else:
                        # print(inp_gen)
                        inp_gen.send(reverse_msg)
                #     pass:
        except StopIteration:
            break


if __name__ == '__main__':
    ddd = iter(range(10))
    ddd1 = reverse_gen_waper(ddd, WaperName.syntax)
    ddd2 = reverse_gen_waper(ddd1, WaperName.expr_calc)
    for i in ddd2:
        if i == 2:
            ddd2.send(ReverseMessage(WaperName.syntax, lambda i: i != 7 and i != 6))
        print(i)