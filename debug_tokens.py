"""Debug tokenization."""

import re

def debug_tokens():
    result = "X=5"
    print(f"Input: '{result}'")
    
    tokens = re.split(r'([&|!=+*/\\[\\]\s-]+)', result)
    print(f"Tokens: {tokens}")
    
    def normalize_token(token):
        print(f"  Processing token: '{token}'")
        if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', token) and token.isascii():
            print(f"    -> identifier, converting to lowercase: '{token.lower()}'")
            return token.lower()
        else:
            print(f"    -> not identifier, keeping as-is")
            return token
    
    normalized_tokens = [normalize_token(token) for token in tokens if token]
    print(f"Normalized tokens: {normalized_tokens}")
    
    result = ''.join(normalized_tokens)
    print(f"Final: '{result}'")

debug_tokens()