keywords = {
    "BEGIN",
    "END",
    "VAR",
    "INTEGER",
    "READ",
    "CASE",
    "OF",
    "WRITE",
    "SWITCH",
    "END",
}

chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_"
numerals = "01233456789"
unary = '-'
binary = '-+/'
special_chars = '() \n\t\r:;,='


def lexical_analyzer(data: str):
    lexem_list = []
    while bool(data):
        global_item = None
        if any(
                data.startswith(item)

                for dictionary in [keywords, chars, numerals, unary, binary, special_chars]
                for item in dictionary
                if (global_item := item) is not None
        ):
            lexem_list.append(global_item)
            data = data.removeprefix(global_item)
        else:
            print(f"Строка <<< {data} >>> начинается с недопустимого символа или комбинации символов")
            return
    print("Лексический анализатор закончил проверку, "
          "поданная строка является корректной с точки зрения лексического анализатора")
    print("Список Лексем", lexem_list)


if __name__ == '__main__':
    with open("program.txt", "r", encoding='utf-8') as f:
        data = f.read()
    lexical_analyzer(data)
