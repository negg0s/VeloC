import sys
import re
from pathlib import Path

def transpile_cpp_to_veloc(cpp_source: str) -> str:
    lines = cpp_source.splitlines()
    veloc_lines = []
    
    for line in lines:
        stripped = line.strip()
        
        # Skip pure boilerplate includes that veloc.h covers
        if stripped.startswith("#include") and any(h in stripped for h in ("<iostream>", "<vector>", "<string>", "<cmath>", "<cstdint>", "<cstdio>")):
            continue
            
        # Transform auto main() or int main()
        line = re.sub(r'\bint\s+main\s*\((.*?)\)', r'pub fn main(\1) -> i32', line)
        line = re.sub(r'\bvoid\s+main\s*\((.*?)\)', r'pub fn main(\1) -> i32', line)
        
        # Transform std::cout << a << b ...; -> println(f"{a}{b}");
        while "std::cout" in line:
            m = re.search(r'std::cout\s*<<\s*([^;]+);', line)
            if not m:
                break
            raw_expr = m.group(1).replace("<< std::endl", "").replace("<< \"\\n\"", "").strip()
            # Split only on << at paren depth 0
            chunks = []
            cur_chunk = []
            depth = 0
            idx = 0
            while idx < len(raw_expr):
                if raw_expr[idx] == '(':
                    depth += 1
                    cur_chunk.append(raw_expr[idx])
                elif raw_expr[idx] == ')':
                    depth -= 1
                    cur_chunk.append(raw_expr[idx])
                elif depth == 0 and raw_expr[idx:idx+2] == "<<":
                    chunks.append("".join(cur_chunk).strip())
                    cur_chunk = []
                    idx += 1
                else:
                    cur_chunk.append(raw_expr[idx])
                idx += 1
            if cur_chunk:
                chunks.append("".join(cur_chunk).strip())

            f_parts = []
            if len(chunks) == 1 and (chunks[0].isalnum() or chunks[0].isdigit() or chunks[0].startswith('"')):
                repl = f'println({chunks[0]});'
            else:
                for c in chunks:
                    if c.startswith('"') and c.endswith('"'):
                        f_parts.append(c.strip('"'))
                    else:
                        f_parts.append(f"{{{c}}}")
                repl = f'println(f"{"".join(f_parts)}");'
            line = line[:m.start()] + repl + line[m.end():]
                
        # Transform do { ... } while (...); -> while (true) { ...; if (!cond) break; }
        line = re.sub(r'\bdo\s*\{([^}]+)\}\s*while\s*\(([^)]+)\)\s*;', r'while (true) { \1; if (!(\2)) break; }', line)

        # Transform variable declarations: auto x = ... -> let mut x = ...
        line = re.sub(r'\bauto\s+([a-zA-Z_]\w*)\s*=', r'let mut \1 =', line)
        line = re.sub(r'\bconst\s+auto\s+([a-zA-Z_]\w*)\s*=', r'let \1 =', line)
        
        # Transform std::vector<T> -> Vec<T>
        line = re.sub(r'std::vector<', r'std::vector<', line)
        
        # Transform NULL -> nullptr
        line = re.sub(r'\bNULL\b', 'nullptr', line)
        
        veloc_lines.append(line)
        
    return "\n".join(veloc_lines)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/from_cpp.py <file.cpp> [-o file.vc]")
        sys.exit(1)
        
    src_file = Path(sys.argv[1])
    if not src_file.exists():
        print(f"Error: {src_file} does not exist")
        sys.exit(1)
        
    out_file = src_file.with_suffix(".vc")
    if "-o" in sys.argv:
        out_file = Path(sys.argv[sys.argv.index("-o") + 1])
        
    cpp_code = src_file.read_text(encoding="utf-8")
    vc_code = transpile_cpp_to_veloc(cpp_code)
    out_file.write_text(vc_code, encoding="utf-8")
    print(f"[VeloC From-C++] Transpiled {src_file.name} -> {out_file.name} successfully.")
