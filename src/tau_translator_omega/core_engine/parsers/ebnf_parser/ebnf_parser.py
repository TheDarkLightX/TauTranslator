"""
Minimal EBNF parser stubs to satisfy legacy tests.
"""

class EBNFTokenizer: ...
class EBNFParser:
    def parse(self, text: str):
        raise NotImplementedError("EBNF parsing is not implemented in this build.")

def create_ebnf_parser():
    return EBNFParser()


