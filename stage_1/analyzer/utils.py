import re

class NLParseError(Exception):
    pass

def parse_nl_query(q: str) -> dict:
    """
    Very small heuristic parser that turns a natural-language query into filters.
    Supported heuristics (examples you requested):
      - "all single word palindromic strings" -> {"word_count": 1, "is_palindrome": True}
      - "strings longer than 10 characters" -> {"min_length": 11}
      - "palindromic strings that contain the first vowel" -> is_palindrome True and contains_character 'a' (heuristic)
      - "strings containing the letter z" -> {"contains_character": "z"}
    Raises NLParseError if it can't produce filters.
    """
    original = q.strip().lower()
    if not original:
        raise NLParseError("empty query")

    parsed = {}
    # single word
    if re.search(r'\b(single word|one word)\b', original):
        parsed['word_count'] = 1

    # palindromic
    if re.search(r'palindrom', original):
        parsed['is_palindrome'] = True

    # strings longer than N characters
    m = re.search(r'longer than (\d+)', original)
    if m:
        n = int(m.group(1))
        parsed['min_length'] = n + 1  # "longer than 10" -> min_length = 11

    # strings shorter than N characters
    m2 = re.search(r'shorter than (\d+)', original)
    if m2:
        n = int(m2.group(1))
        parsed['max_length'] = n - 1 if n > 0 else 0

    # containing the letter X or containing the letter 'z'
    m3 = re.search(r'containing the letter (\w)', original)
    if m3:
        parsed['contains_character'] = m3.group(1)

    m4 = re.search(r'contain the letter (\w)', original)
    if m4:
        parsed['contains_character'] = m4.group(1)

    # "contain the first vowel" heuristic -> 'a'
    if 'first vowel' in original:
        parsed['contains_character'] = parsed.get('contains_character', 'a')

    # "strings containing the letter z" exact phrase
    if re.search(r'\bcontaining.*z\b', original):
        parsed['contains_character'] = 'z'

    if not parsed:
        raise NLParseError("unable to parse natural language query")

    return {
        "original": q,
        "parsed_filters": parsed
    }
