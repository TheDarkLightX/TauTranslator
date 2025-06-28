from lark import Transformer

class SimpleMathTransformer(Transformer):
    def start(self, items):
        return " ; ".join(items)

    def statement(self, items):
        name = items[0]
        value = items[1]
        return f"let {name} = {value}"

    def expr(self, items):
        return " ".join(str(i) for i in items)

    def term(self, items):
        return " ".join(str(i) for i in items)

    def parenthesized_expr(self, items):
        return f"( {items[0]} )"

    def factor(self, items):
        return items[0]

    def atom(self, items):
        return items[0]

    def CNAME(self, token):
        return token.value

    def NUMBER(self, token):
        return token.value

    def OP_PLUS_MINUS(self, token):
        return token.value

    def OP_MUL_DIV(self, token):
        return token.value
