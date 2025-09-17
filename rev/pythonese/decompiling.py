import sys, os, marshal, dis, types, io
from pathlib import Path

def load_codeobj(pyc_path):
    data = open(pyc_path, "rb").read()
    header_len = 16 if len(data) > 16 else 12
    return marshal.loads(data[header_len:])

def text_for_function(name, fn):
    out = []
    co = fn.__code__
    out.append(f"Function: {name}")
    out.append(f"co_name: {co.co_name}")
    out.append(f"co_filename: {co.co_filename}")
    out.append(f"co_firstlineno: {co.co_firstlineno}")
    out.append(f"co_argcount: {getattr(co, 'co_argcount', 'N/A')}")
    out.append(f"co_posonlyargcount: {getattr(co, 'co_posonlyargcount', 'N/A')}")
    out.append(f"co_kwonlyargcount: {getattr(co, 'co_kwonlyargcount', 'N/A')}")
    out.append("")
    out.append("=== DISASSEMBLY ===")
    sio = io.StringIO()
    try:
        dis.dis(fn, file=sio)
        out.append(sio.getvalue())
    except Exception as e:
        out.append(f"(disassembly failed: {e})")
    out.append("")
    out.append("=== co_names / co_varnames ===")
    out.append(f"co_names: {co.co_names}")
    out.append(f"co_varnames: {co.co_varnames}")
    out.append("")
    out.append("=== co_consts (truncated where long) ===")
    for i, c in enumerate(co.co_consts):
        if isinstance(c, (bytes, bytearray)):
            out.append(f"[{i}] bytes len={len(c)} repr={repr(c[:80])}...")
        else:
            rep = repr(c)
            if len(rep) > 500:
                rep = rep[:500] + "...(truncated)"
            out.append(f"[{i}] {rep}")
    out.append("")
    out.append("=== Integer tuples found (useful arrays) ===")
    for i, c in enumerate(co.co_consts):
        if isinstance(c, (tuple, list)) and c and all(isinstance(x, int) for x in c):
            out.append(f"CONST_INDEX {i}: {list(c)}")
    return "\n".join(out)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 simple_decompile.py bytecode.pyc")
        return
    pyc_path = Path(sys.argv[1])
    if not pyc_path.exists():
        print("File not found:", pyc_path)
        return

    mod_code = load_codeobj(str(pyc_path))

    ns = {}
    try:
        exec(mod_code, ns, ns)
    except Exception as e:
        print("Warning: executing module raised:", e)

    outdir = Path("decompiled_funcs")
    outdir.mkdir(exist_ok=True)

    funcs = [(k, v) for k, v in ns.items() if isinstance(v, types.FunctionType)]
    if not funcs:
        try:
            with open(outdir / "module_consts.txt", "w", encoding="utf-8") as fh:
                fh.write("Module code object repr:\n")
                fh.write(repr(mod_code) + "\n\n")
                fh.write("Top-level co_consts:\n")
                for i, c in enumerate(mod_code.co_consts):
                    fh.write(f"[{i}] {repr(c)[:500]}\n")
            print("No function objects found; wrote module_consts.txt")
            return
        except Exception as e:
            print("Failed to write fallback module_consts:", e)
            return

    for name, fn in sorted(funcs):
        fname = outdir / f"{name}.txt"
        try:
            txt = text_for_function(name, fn)
            with open(fname, "w", encoding="utf-8") as fh:
                fh.write(txt)
            print("Wrote:", fname)
        except Exception as e:
            print("Failed writing for", name, ":", e)

    print("\nDone. Check the 'decompiled_funcs' directory for per-function .txt files.")

if __name__ == "__main__":
    main()
