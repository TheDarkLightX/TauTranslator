import sys
import math
from collections import Counter
import os

def calculate_shannon_entropy(file_path: str) -> float:
    """Calculates the Shannon entropy of a file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
        if not text:
            return 0.0
        
        counts = Counter(text)
        total_chars = len(text)
        entropy = 0.0
        
        for count in counts.values():
            probability = count / total_chars
            entropy -= probability * math.log2(probability)
            
        return entropy
    except FileNotFoundError:
        # Suppress error for files that might be deleted during processing
        return 0.0
    except Exception as e:
        print(f"Error processing {file_path}: {e}", file=sys.stderr)
        return 0.0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python calculate_entropy.py <dir1> <file1> <dir2> ...", file=sys.stderr)
        sys.exit(1)
        
    input_paths = sys.argv[1:]
    file_paths = []

    for path in input_paths:
        if os.path.isdir(path):
            for root, _, files in os.walk(path):
                for file in files:
                    if file.endswith('.py'):
                        file_paths.append(os.path.join(root, file))
        elif os.path.isfile(path) and path.endswith('.py'):
            file_paths.append(path)

    results = []
    
    for path in file_paths:
        entropy = calculate_shannon_entropy(path)
        if entropy > 0:
            results.append((path, entropy))
            
    # Sort results by entropy in descending order
    results.sort(key=lambda x: x[1], reverse=True)
    
    print("Shannon Entropy Report (High to Low):")
    for path, entropy in results:
        print(f"{entropy:.4f}\t{path}")
