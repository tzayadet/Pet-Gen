from pathlib import Path
import re
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
html = (root / "index.html").read_text(encoding="utf-8")

scripts = re.findall(r"<script\b[^>]*>([\s\S]*?)</script\s*>", html, re.IGNORECASE)
if len(scripts) != 1:
    raise SystemExit(f"Expected one inline application script, found {len(scripts)}")

if re.search(r"<script\b[^>]+src=[\"']https?://", html, re.IGNORECASE):
    raise SystemExit("Unexpected remote JavaScript dependency")

ids = re.findall(r"\bid=[\"']([^\"']+)[\"']", html, re.IGNORECASE)
duplicates = sorted({value for value in ids if ids.count(value) > 1})
if duplicates:
    raise SystemExit(f"Duplicate HTML IDs: {duplicates}")

with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
    handle.write(scripts[0])
    script_path = Path(handle.name)

try:
    subprocess.run(["node", "--check", str(script_path)], check=True)
finally:
    script_path.unlink(missing_ok=True)

print(f"{root.name}: HTML and JavaScript validation passed.")
