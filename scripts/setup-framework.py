import json, shutil, subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[1]
framework=root/'vendor/adapt-framework'
shutil.copy(root/'adapt-npm.package-lock.json',framework/'package-lock.json')
plugins=json.loads((root/'adapt-plugins.lock.json').read_text())
(framework/'adapt.json').write_text(json.dumps({'dependencies':plugins},indent=2))
subprocess.run(['npm','ci','--omit=dev','--omit=optional','--no-audit','--no-fund'],cwd=framework,check=True)
subprocess.run(['npx','--yes','adapt-cli@3.4.0','install'],cwd=framework,check=True)
