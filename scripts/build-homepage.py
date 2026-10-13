"""Build the static anonymous entry from the same content used by Jekyll."""
from pathlib import Path
import hashlib
import re

root = Path(__file__).resolve().parents[1]

def asset_version(path):
    return hashlib.sha256((root / path).read_bytes()).hexdigest()[:12]

# The embedded UI carries its own styles and must refresh with the page.
loader_path = root / "assets/home-demo.js"
loader = loader_path.read_text()
loader, count = re.subn(
    r"loadScript\('embed-ui\.js(?:\?[^']*)?'\)",
    f"loadScript('embed-ui.js?v={asset_version('rally/embed-ui.js')}')",
    loader,
)
assert count == 1
if loader != loader_path.read_text():
    loader_path.write_text(loader)

# Update the shared Jekyll layout as well as the static preview. Fixed version
# strings let browsers combine fresh HTML with stale styles after a deployment.
layout_path = root / "_layouts/project.html"
layout = layout_path.read_text()
layout = re.sub(
    r'(href|src)="\./(assets/[^"?]+\.(?:css|js))(?:\?[^" ]*)?"',
    lambda m: f'{m[1]}="./{m[2]}?v={asset_version(m[2])}"',
    layout,
)
if layout != layout_path.read_text():
    layout_path.write_text(layout)
layout = layout.replace("{% include project-hero.html %}", (root / "_includes/project-hero.html").read_text())
content = (root / "_includes/project-home.html").read_text()
assert layout.count("{{ content }}") == 1
(root / "index.html").write_text(layout.replace("{{ content }}", content))
print("Built index.html from the shared project layout and content.")
