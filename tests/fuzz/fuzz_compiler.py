import os
import sys
import random
import glob
import hashlib
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from lexer import Lexer, LexerError
from parser import Parser, ParseError, MultiParseError
from diagnostics import DiagnosticReporter

FUZZ_DIR = ROOT_DIR / "tests" / "fuzz"
CORPUS_DIR = FUZZ_DIR / "corpus"
CRASHES_DIR = FUZZ_DIR / "crashes"
CRASHES_DIR.mkdir(parents=True, exist_ok=True)

class MutationFuzzer:
    def __init__(self, seed: int = 1337):
        self.rng = random.Random(seed)
        self.corpus: list[str] = []
        self._load_corpus()

    def _load_corpus(self):
        for f in glob.glob(str(CORPUS_DIR / "*.vc")):
            self.corpus.append(Path(f).read_text(encoding="utf-8", errors="ignore"))
        if not self.corpus:
            self.corpus.append("fn main() -> i32 { return 0; }")

    def mutate(self, text: str) -> str:
        data = list(text)
        if not data:
            return "fn main() {}"
        
        mut_type = self.rng.randint(0, 5)
        pos = self.rng.randint(0, len(data) - 1)

        if mut_type == 0:
            # Random character insertion
            char = self.rng.choice("abcdefghijklmnopqrstuvwxyz0123456789{}();:=><+-/*\"'_ \n\t\x00\xff")
            data.insert(pos, char)
        elif mut_type == 1 and len(data) > 1:
            # Character deletion
            del data[pos]
        elif mut_type == 2:
            # Character substitution
            char = self.rng.choice("!@#$%^&*()_+-=[]{}|;':\",./<>?`~")
            data[pos] = char
        elif mut_type == 3:
            # Token duplication
            token = self.rng.choice(["let ", "mut ", "fn ", "match ", "if ", "else ", "return ", "SOA ", "{", "}", ";"])
            data.insert(pos, token)
        elif mut_type == 4:
            # Extreme recursion/nesting test
            nested = "(((((" * 10 + "1" + ")))))" * 10
            data.insert(pos, nested)
        elif mut_type == 5:
            # Splice with another corpus entry
            other = self.rng.choice(self.corpus)
            split_at = self.rng.randint(0, len(other))
            data.extend(other[split_at:split_at + 20])

        return "".join(data)

def run_fuzzer(iterations: int = 500):
    print("==================================================")
    print("           VeloC Compiler Robustness Fuzzer       ")
    print("==================================================")
    print(f"Target: Running {iterations} mutation fuzzing iterations...")
    print("Invariant: Lexer and Parser must NEVER panic or raise unhandled crashes.\n")

    fuzzer = MutationFuzzer()
    crashes = 0
    clean_parses = 0
    clean_errors = 0

    for i in range(1, iterations + 1):
        seed_text = fuzzer.rng.choice(fuzzer.corpus)
        mutated = fuzzer.mutate(seed_text)

        try:
            tokens = Lexer(mutated, f"<fuzz_{i}>").tokenize()
            parser = Parser(tokens, mutated, f"<fuzz_{i}>")
            parser.parse_program()
            clean_parses += 1
        except (LexerError, ParseError, MultiParseError):
            clean_errors += 1
        except Exception as crash_err:
            crashes += 1
            h = hashlib.sha256(mutated.encode("utf-8", errors="ignore")).hexdigest()[:10]
            crash_file = CRASHES_DIR / f"crash_{h}.vc"
            crash_file.write_text(mutated, encoding="utf-8")
            print(f"  [CRASH DETECTED] Iteration #{i}: {type(crash_err).__name__}: {crash_err}")
            print(f"  Reproducer saved to: {crash_file}")
            break

        if i % 100 == 0 or i == iterations:
            print(f"  [Progress] Iteration {i:>5}/{iterations}: Clean parses={clean_parses}, Clean errors={clean_errors}, Crashes={crashes}")

    print("==================================================")
    if crashes == 0:
        print(f"Fuzzing Passed: 0 crashes across {iterations} iterations (100% panic-free)")
        print("==================================================")
        return True
    else:
        print(f"Fuzzing Failed: {crashes} compiler crashes detected!")
        print("==================================================")
        return False

if __name__ == "__main__":
    iters = int(sys.argv[1]) if len(sys.argv) > 1 else 500
    success = run_fuzzer(iters)
    sys.exit(0 if success else 1)
