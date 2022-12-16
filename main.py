from interpreter.main_interpreter import interpreter
from syntax_analyzer.rules.raw_rules import raw_rules_dict

if __name__ == '__main__':
    with open("program.txt", "r", encoding='utf-8') as f:
        data = f.read()

    variables_dict = dict()
    for i in interpreter(data, raw_rules_dict, variables_dict):
        pass
