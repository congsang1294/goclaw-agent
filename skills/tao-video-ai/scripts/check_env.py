#!/usr/bin/env python3
"""
check_env.py — Kiểm tra môi trường cho skill tao-video-ai.

Kiểm tra:
  - Python version
  - API keys (OPENAI_API_KEY, ANTHROPIC_API_KEY, HIGGSFIELD_API_KEY)
  - Required packages (openai, anthropic, dotenv)
  - Product photos directory
  - Output directory

Usage:
    python scripts/check_env.py
"""

import importlib
import json
import os
import sys
import subprocess
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent

try:
    from dotenv import load_dotenv
    load_dotenv(SKILL_DIR / "scripts" / ".env")
except ImportError:
    pass

# ---------- checks ----------

def check_python():
    print(f"  Python: {sys.version.split()[0]}")
    return True

def check_api_key(name, label):
    val = os.environ.get(name, "")
    if val:
        short = val[:8] + "..." if len(val) > 12 else val
        print(f"  {label}: ✅ {short}")
        return True
    else:
        print(f"  {label}: ⬜ (not set)")
        return False

def check_package(name, pip_name=None):
    try:
        mod = importlib.import_module(name)
        ver = getattr(mod, "__version__", "?")
        print(f"  {name}: ✅ v{ver}")
        return True
    except ImportError:
        print(f"  {name}: ❌ not installed — pip install {pip_name or name}")
        return False

def check_dir(path, label):
    p = Path(path)
    if p.exists():
        files = [f for f in p.iterdir() if f.is_file()]
        print(f"  {label}: ✅ ({len(files)} files)")
        return True
    else:
        print(f"  {label}: ❌ not found at {p}")
        return False

def check_env_file():
    env_path = SKILL_DIR / "scripts" / ".env"
    if env_path.exists():
        lines = [l for l in env_path.read_text().splitlines() if l.strip() and not l.startswith("#")]
        print(f"  .env: ✅ ({len(lines)} config lines)")
        return True
    else:
        print(f"  .env: ❌ not found at {env_path}")
        return False

# ---------- main ----------

def main():
    print("=" * 50)
    print("  tao-video-ai — Environment Check")
    print("=" * 50)

    print("\n--- System ---")
    check_python()

    print("\n--- API Keys ---")
    has_llm = check_api_key("OPENAI_API_KEY", "OpenAI")
    has_claude = check_api_key("ANTHROPIC_API_KEY", "Claude")
    check_api_key("HIGGSFIELD_API_KEY", "Higgsfield")

    print("\n--- Packages ---")
    check_package("openai")
    check_package("anthropic")
    check_package("dotenv", "python-dotenv")

    print("\n--- Directories ---")
    check_dir(SKILL_DIR / "assets", "assets/")
    check_dir(SKILL_DIR / "references", "references/")
    check_dir(SKILL_DIR / "scripts", "scripts/")
    check_dir(SKILL_DIR / "output", "output/")

    # product-photos — tìm ở nhiều nơi
    print("\n--- Product Photos ---")
    candidates = [
        SKILL_DIR / "product-photos",
        SKILL_DIR.parent / "product-photos",
        SKILL_DIR.parent.parent / "product-photos",
        Path.cwd() / "product-photos",
    ]
    found = False
    for c in candidates:
        if c.exists() and any(c.iterdir()):
            files = list(c.rglob("*"))
            images = [f for f in files if f.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")]
            print(f"  product-photos: ✅ ({len(images)} ảnh tại {c})")
            found = True
            break
    if not found:
        print(f"  product-photos: ❌ not found (searched {len(candidates)} locations)")

    print("\n--- Test Scripts ---")
    scripts = ["gen-prompt.py", "list-images.py", "upload-higgsfield.py"]
    all_ok = True
    for s in scripts:
        sp = SKILL_DIR / "scripts" / s
        if sp.exists():
            # syntax check
            result = subprocess.run(
                [sys.executable, "-c", f"import ast; ast.parse(open('{sp}').read())"],
                capture_output=True, text=True,
            )
            if result.returncode == 0:
                print(f"  {s}: ✅ syntax OK")
            else:
                print(f"  {s}: ⚠️ syntax error — {result.stderr.strip()[:80]}")
                all_ok = False
        else:
            print(f"  {s}: ❌ not found")
            all_ok = False

    print("\n" + "=" * 50)
    if has_llm or has_claude:
        print("  Status: ✅ Sẵn sàng chạy pipeline")
    else:
        print("  Status: ⚠️ Cần set API key (.env)")
    print("=" * 50)


if __name__ == "__main__":
    main()
