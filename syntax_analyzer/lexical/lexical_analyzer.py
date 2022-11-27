from syntax_analyzer.lexical.terminals import keywords, chars, numerals, unary, binary, special_chars, blanks, \
    TERMINALS, BLANKS_ENUM, OPTIONAL_BLANKS_ENUM


def lexical_analyzer(data: str):
    # lexem_list = []
    last_item = OPTIONAL_BLANKS_ENUM(None)
    while bool(data):
        global_item = None

        if any(
                data.startswith(item)

                for dictionary in [keywords, chars, numerals, unary, binary, special_chars, blanks]
                for item in dictionary
                if (global_item := item) is not None
        ):
            if TERMINALS[global_item].name in [i.name for i in BLANKS_ENUM] and last_item.name in [i.name for i in BLANKS_ENUM]:
                last_item = TERMINALS[global_item]
                data = data.removeprefix(global_item)
                continue
            yield TERMINALS[global_item]
            last_item = TERMINALS[global_item]
            # lexem_list.append(global_item)
            data = data.removeprefix(global_item)
        else:
            raise SyntaxError(f"Строка <<<{data}>>> начинается с недопустимого символа или комбинации символов")
            # return
    # print("Лексический анализатор закончил проверку, "
    #           "поданная строка является корректной с точки зрения лексического анализатора")

if __name__ == '__main__':
    with open("../program.txt", "r", encoding='utf-8') as f:
        data = f.read()
    print(*lexical_analyzer(data))
