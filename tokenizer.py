import re

token_specification = [
    ('NUMBER', r'\d+(\.\d*)?'),  # Integer or decimal number
    ("COMPARE", r'==|!=|>=|<='),
    ('ASSIGN', r'='),  # Assignment operator
    ('END', r';'),  # Statement terminator
    ('ID', r'[A-Za-z_]\w*'),  # Identifiers (variable names, function names)
    ('STRING', r'"[^"]*"'),  # String literals
    ('OP', r'[+*/><-]'),  # Operators
    ('LBRACE', r'\{'),  # Left brace
    ('RBRACE', r'\}'),  # Right brace
    ('LPAREN', r'\('),  # Left parenthesis
    ('RPAREN', r'\)'),  # Right parenthesis
    ('COMMA', r','),  # Comma
    ('INDEX', r'\.'),
    ('SKIP', r'[ \t]+'),  # Skip spaces and tabs
]

keywords = {'create', 'var', 'define', 'if', "repeat_until", "repeat", "list"}
# rest of the initial keywords 'else', 'return', 'exit', 'list', 'wait', 'struct'

tok_regex = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in token_specification)


def tokenize(code):
    tokens = []
    for match in re.finditer(tok_regex, code):
        kind = match.lastgroup
        value = match.group()
        if kind == 'ID' and value in keywords:
            kind = 'KEYWORD'
        elif kind == 'NUMBER':
            value = float(value) if '.' in value else int(value)
        elif kind == 'SKIP' or kind == 'COMMENT':
            continue
        tokens.append((kind, value))
    return tokens
