"""Debug final case issue."""

import re

def debug_case_final():
    result = "X=5"
    print(f"Input: '{result}'")
    
    # My current logic
    words = re.findall(r'\S+', result)
    print(f"Words: {words}")
    
    normalized_words = []
    
    for word in words:
        print(f"\nProcessing word: '{word}'")
        
        # Remove operators to check if it's ASCII
        clean_word = word.replace('=', '').replace('&', '').replace('|', '').replace('!', '').replace('[', '').replace(']', '')
        print(f"Clean word: '{clean_word}'")
        print(f"Is ASCII: {clean_word.isascii()}")
        
        if clean_word.isascii():
            # Check if it's an identifier (letters/numbers/underscore)
            print(f"Checking if '{word}' matches identifier pattern")
            if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', word):
                print(f"Is identifier, converting to lowercase")
                normalized_words.append(word.lower())
            else:
                print(f"Not identifier, keeping as-is")
                normalized_words.append(word)
        else:
            normalized_words.append(word)
    
    result = ' '.join(normalized_words) if normalized_words else result
    print(f"Final: '{result}'")

debug_case_final()