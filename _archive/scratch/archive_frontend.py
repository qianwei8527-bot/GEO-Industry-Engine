import os, pathlib
root = pathlib.Path("D:/GEO-Industry-Engine")
src = pathlib.Path("D:/GEO-Industry-Engine/frontend ")
renamed = root / "frontend_old_20260811"
dst = pathlib.Path("D:/GEO-Industry-Engine/_archive/scratch/frontend_old_20260811")
print("src exists:", src.exists(), "| renamed exists:", renamed.exists(), "| dst exists:", dst.exists(), flush=True)
if not src.exists():
    print("nothing to do", flush=True)
elif renamed.exists() or dst.exists():
    print("target already exists; abort", flush=True)
else:
    try:
        os.rename(str(src), str(renamed))
        print("step1 rename ok", flush=True)
        os.rename(str(renamed), str(dst))
        print("step2 move into archive ok", flush=True)
    except Exception as e:
        print("move failed:", repr(e), flush=True)
print("final -> src:", src.exists(), "| dst:", dst.exists(), flush=True)
