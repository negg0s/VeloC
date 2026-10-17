# scripts/fix_snippets.py
from pathlib import Path

for root in [Path('docs/en/book'), Path('docs/ru/book')]:
    for p in root.glob('*.md'):
        txt = p.read_text(encoding='utf-8')
        txt = txt.replace('println(', 'printf(')
        # make sure format strings have \n
        txt = txt.replace('Hello, VeloC!"', 'Hello, VeloC!\\n"')
        txt = txt.replace('Привет, VeloC!"', 'Привет, VeloC!\\n"')
        txt = txt.replace('First: %d"', 'First: %d\\n"')
        txt = txt.replace('Первый элемент: %d"', 'Первый элемент: %d\\n"')
        txt = txt.replace('Fib(10) = %d"', 'Fib(10) = %d\\n"')
        p.write_text(txt, encoding='utf-8')

print("Snippets normalized.")
