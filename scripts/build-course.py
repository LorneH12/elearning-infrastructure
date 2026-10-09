"""Copy independent content/extension into Adapt and build a web test package."""
import argparse, json, shutil, subprocess, zipfile
from pathlib import Path
root = Path(__file__).resolve().parents[1]
framework = root / 'vendor/adapt-framework'
parser = argparse.ArgumentParser()
parser.add_argument('--format', choices=['web','scorm'], default='web')
args = parser.parse_args()
shutil.copytree(root/'course-source', framework/'src/course', dirs_exist_ok=True)
extension = framework/'src/extensions/adapt-portfolio-xapi'
if extension.exists(): shutil.rmtree(extension)
if args.format == 'web':
    shutil.copytree(root/'extensions/adapt-portfolio-xapi', extension)
config_path = framework/'src/course/config.json'
config = json.loads(config_path.read_text())
config['_spoor'] = {'_isEnabled':args.format == 'scorm', '_advancedSettings':{'_scormVersion':'1.2'}}
config_path.write_text(json.dumps(config,indent=2))
output = root/'dist'/args.format
subprocess.run(['npx','grunt','build'], cwd=framework, check=True)
if output.exists(): shutil.rmtree(output)
shutil.copytree(framework/'build',output)
if args.format == 'scorm':
    with zipfile.ZipFile(root/'dist/infrastructure-scorm12.zip','w',zipfile.ZIP_DEFLATED) as archive:
        for file in output.rglob('*'):
            if file.is_file(): archive.write(file,file.relative_to(output))
