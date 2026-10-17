import json
from pathlib import Path

p = Path(".cache/diag_veloc.json")
if p.exists():
    data = json.loads(p.read_text(encoding="utf-8"))
    events = [e for e in data.get("traceEvents", []) if "dur" in e]
    events.sort(key=lambda x: x["dur"], reverse=True)
    print("=" * 80)
    print("         Clang -ftime-trace Analysis on include/veloc.h                         ")
    print("=" * 80)
    headers = {}
    instantiations = {}

    for e in events:
        name = e.get("name", "")
        dur = e.get("dur", 0) / 1000.0 # ms
        detail = e.get("args", {}).get("detail", "")
        if name == "Source":
            headers[detail] = headers.get(detail, 0) + dur
        elif name == "InstantiateFunction" or name == "InstantiateClass":
            instantiations[detail] = instantiations.get(detail, 0) + dur

    print("\n[Top 15 Included Header Files by Parse/Processing Time]:")
    sorted_headers = sorted(headers.items(), key=lambda x: x[1], reverse=True)
    for h, d in sorted_headers[:15]:
        print(f"  * {d:6.1f} ms : {Path(h).name:<30} ({h[-50:]})")

    print("\n[Top 15 Expensive Template Instantiations]:")
    sorted_inst = sorted(instantiations.items(), key=lambda x: x[1], reverse=True)
    for inst, d in sorted_inst[:15]:
        print(f"  * {d:6.1f} ms : {inst[:70]}")
    print("=" * 80)
