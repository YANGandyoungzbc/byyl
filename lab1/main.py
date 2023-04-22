"""
DFA： 有穷自动机
1. 初始化5个参数
    1. states : list            状态集
    2. input_symbols : list     字母表
    3. start_state : str        起始状态
    4. final_states : list      终止，接受状态集
    5. trans : dict             转移函数 (2维字典）
2. 读入一个串 input_str
3. input_str 与 input_symbols, 查看是否有非法字符
4. 遍历 input_str 获取 next_state
5. 查看最终的 final_state 是否在 final_states 中
    - 是
    - 不是
"""


class DFA:
    def __init__(self, states: list, input_symbols: list,
                 start_state: str, final_states: list, trans: dict):
        self.states = states
        self.input_symbols = input_symbols
        self.start_state = start_state
        self.final_states = final_states
        self.trans = trans

    def input_str(self, input_str):
        current_state = self.start_state
        for s in input_str:
            if s not in self.input_symbols:
                print("有非法字符")
                return False
        for s in input_str:
            current_state = self.get_next_state(current_state, s)
        final_state = current_state
        if final_state in self.final_states:
            print("是")
            return True
        else:
            print("不是")
            return False

    def get_next_state(self, current_state, input_str):
        current_trans = self.trans[current_state]
        next_state = current_trans[input_str]
        print(f"{current_state}--{input_str}--{next_state}")
        return next_state


if __name__ == '__main__':
    dfa1 = DFA(
        states=['S', 'U', 'V', 'Q'],
        start_state='S',
        final_states=['Q'],
        input_symbols=['a', 'b'],
        trans={
            'S': {
                'a': 'U',
                'b': 'V'
            },
            'U': {
                'a': 'Q',
                'b': 'V'
            },
            'V': {
                'a': 'U',
                'b': 'Q'
            },
            'Q': {
                'a': 'Q',
                'b': 'Q'
            }
        }
    )
    dfa1.input_str("aaa")
    dfa1.input_str("aba")
    dfa1.input_str("bba")
    dfa1.input_str("bbb")
    dfa1.input_str("abababbabaaaabbbaabba")
    dfa1.input_str("bab")
