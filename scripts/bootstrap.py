"""Fetch recorded upstream revisions without touching other repositories."""
import json, subprocess, sys
from pathlib import Path
root = Path(__file__).resolve().parents[1]
lock = json.loads((root/'upstreams.lock.json').read_text())
for name, item in lock.items():
    target = root/'vendor'/name
    if not target.exists():
        target.mkdir(parents=True)
        subprocess.run(['git','init',str(target)],check=True)
        subprocess.run(['git','remote','add','origin',item['url']],cwd=target,check=True)
        subprocess.run(['git','fetch','--depth','1','origin',item['commit']],cwd=target,check=True)
        subprocess.run(['git','checkout','--detach',item['commit']],cwd=target,check=True)
    actual = subprocess.check_output(['git','rev-parse','HEAD'],cwd=target,text=True).strip()
    if actual != item['commit']: sys.exit(f'{name}: existing checkout differs; refusing to overwrite')
print('Upstream revisions verified. See README for runtime setup.')
