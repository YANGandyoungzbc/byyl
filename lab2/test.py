import re
from pprint import pprint
from tabulate import tabulate

"""
{
    "E": [["T","E"]],
    "E'": [["+","T","E'"],["epsilon"]],
    "T": [["F","T'"]],
    "T'":[["*","F","T'"],["epsilon]],
    "F": [["i"],["(","E",")"]]
}
"""


class LL:
    def __init__(self, grammer: str, input_str: str, start: str = 'E'):
        """
        初始化LL
        :param grammer: 语法的文件名
        """
        self.filename = grammer
        self.terminals = self.getTerminals()
        self.nonterminals = self.getNonterminals()
        self.start = start
        self.productions = self.getProductions()
        self.first = self.init_first()
        self.follow = self.getFollow()
        self.predictive_table = self.init_predictive_table()
        self.input_str = input_str

    def getTerminals(self):
        with open(self.filename, 'r') as f:
            data = f.read()

        terminals_regex = r'[a-z()*+]+'

        terminals = re.findall(terminals_regex, data)
        terminals = list(set(terminals))
        terminals.append('$')

        return terminals

    def getNonterminals(self):
        with open(self.filename, 'r') as f:
            data = f.read()

        nonterminals_regex = r'[A-Z][\']?'

        nonterminals = re.findall(nonterminals_regex, data)
        nonterminals = list(set(nonterminals))  # 去重

        return nonterminals

    def getProductions(self):
        productions = {}
        with open(self.filename, 'r') as f:
            data = f.read()
        for line in data.split('\n'):
            production_right = []  # 初始化右部
            # 忽略空行
            if not line:
                continue
            left, right = line.strip().split(' -> ')
            symbols = right.split()
            if '|' in symbols:
                idx = symbols.index('|')
                lhs = symbols[:idx]
                rhs = symbols[idx + 1:]
                production_right.append(lhs)
                production_right.append(rhs)
            else:
                production_right.append(symbols)
                # production = symbols
            productions[left] = production_right
        return productions

    def getFirst(self):
        first = {}

        for terminal in self.terminals:
            first[terminal] = set([terminal])

        for nonterminal in self.nonterminals:
            first[nonterminal] = set()

        while True:
            updated = False

            for nonterminal in self.nonterminals:
                for production in self.productions[nonterminal]:
                    for symbol in production:
                        if symbol in self.terminals:
                            if symbol not in first[nonterminal]:
                                first[nonterminal].add(symbol)
                                updated = True
                            break
                        elif symbol in self.nonterminals:
                            for f in first[symbol]:
                                if f not in first[nonterminal]:
                                    first[nonterminal].add(f)
                                    updated = True
                            if 'epsilon' not in first[symbol]:
                                break
                    else:
                        if 'epsilon' not in first[nonterminal]:
                            first[nonterminal].add('epsilon')
                            updated = True

            if not updated:
                break

        return first

    def init_first(self):
        first = self.getFirst()
        for k in self.terminals:
            first.pop(k)
        return first

    def getFollow(self):
        first = self.getFirst()
        follow = {nonterminal: set() for nonterminal in self.nonterminals}
        follow[self.start] = set(['$'])

        while True:
            updated = False

            for nonterminal in self.nonterminals:
                for production in self.productions[nonterminal]:
                    for i in range(len(production)):
                        symbol = production[i]
                        if symbol in self.nonterminals:
                            j = i + 1
                            while j < len(production) and 'epsilon' in first[production[j]]:
                                for f in first[production[j]] - {'epsilon'}:
                                    if f not in follow[symbol]:
                                        follow[symbol].add(f)
                                        updated = True
                                j += 1
                            if j == len(production):
                                for f in follow[nonterminal]:
                                    if f not in follow[symbol]:
                                        follow[symbol].add(f)
                                        updated = True
                            elif production[j] in self.terminals:
                                if production[j] not in follow[symbol]:
                                    follow[symbol].add(production[j])
                                    updated = True
                            else:
                                for f in first[production[j]]:
                                    if f not in follow[symbol]:
                                        follow[symbol].add(f)
                                        updated = True
                                if 'epsilon' in first[production[j]]:
                                    for f in follow[nonterminal]:
                                        if f not in follow[symbol]:
                                            follow[symbol].add(f)
                                            updated = True
            if not updated:
                break

        return follow

    def init_predictive_table(self):
        table = self.build_predictive_table()
        for key, value in table.items():
            if 'epsilon' in value:
                del value['epsilon']
        return table

    def print_predictive_table(self):
        dict = self.predictive_table
        t = []
        for x, y in dict.items():
            row = [x]
            for s in ['i', '+', '*', '(', ')', '$']:
                if s in y:
                    value = ' '.join(map(str, y[s]))
                    row.append(value)
                else:
                    row.append('')
            t.append(row)
        headers = ['', 'i', '+', '*', '(', ')', '$']
        print(tabulate(t, headers, tablefmt='rounded_grid'))

    def build_predictive_table(self):
        productions = self.productions
        first = self.getFirst()
        follow = self.getFollow()
        table = {}
        for A in productions:
            table[A] = {}
            for a in first[A]:
                table[A][a] = productions[A]  # 添加所有以 A 开头的产生式
            if 'epsilon' in first[A]:
                for b in follow[A]:
                    table[A][b] = [['epsilon']]  # 添加 Follow(A) 中的所有终结符
            for alpha in productions[A]:
                if alpha != ['epsilon']:
                    for a in first[alpha[0]]:
                        if a != 'epsilon':
                            table[A][a] = alpha  # 添加 alpha 的所有 First 集符号
                    if 'epsilon' in first[alpha[0]]:
                        for b in follow[A]:
                            table[A][b] = alpha  # 添加 alpha 推导出空串的 Follow 集符号
        return table

    def analyzeStack(self, input_str: str):
        terminals = self.terminals
        table = self.predictive_table
        stack = ['$', self.start]
        input_str += '$'
        index = 0
        parse_steps = []
        while stack:
            top = stack[-1]
            if top in terminals:
                if top == '$' and input_str[index] == '$':
                    parse_steps.append((''.join(stack), input_str[index:], 'Accept'))
                    break
                if top == input_str[index]:
                    stack.pop()
                    parse_steps.append((''.join(stack), input_str[index:], f'Match {input_str[index]}'))
                    index += 1
                else:
                    return None
            else:
                production = table[top][input_str[index]]
                if production is None:
                    return None
                stack.pop()
                parse_steps.append((''.join(stack), input_str[index:], f"{top} -> {production}"))
                for symbol in reversed(production):
                    if symbol != ['epsilon']:
                        stack.append(symbol)
        return parse_steps

    def print_AnalyzeStack(self):
        analyzeStack = self.analyzeStack(self.input_str)
        print(tabulate(analyzeStack, headers=['Analyze Stack', 'Remaining String', 'Production'],
                       tablefmt="rounded_grid"))


if __name__ == '__main__':
    l = LL('grammar', 'i+i*i')
    print(f'terminals:{l.terminals}')
    print(f'nonterminals:{l.nonterminals}')
    d = l.productions
    print('Productions:')
    pprint(d)
    first = l.first
    follow = l.follow
    print('first set:')
    pprint(first)
    print('follow set:')
    pprint(follow)
    print("=================================================")
    # predictive_table = l.predictive_table
    # pprint(predictive_table)
    l.print_predictive_table()
    l.print_AnalyzeStack()
