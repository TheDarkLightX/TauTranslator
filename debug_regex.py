"""Debug regex split."""

import re

pattern = r'([&|!=+*/\\[\\]\s-]+)'
text = "X=5"

print(f"Pattern: {pattern}")
print(f"Text: {text}")

result = re.split(pattern, text)
print(f"Split result: {result}")

# Try a simpler pattern
pattern2 = r'([=&|!+*/-])'
result2 = re.split(pattern2, text)
print(f"Simpler pattern result: {result2}")