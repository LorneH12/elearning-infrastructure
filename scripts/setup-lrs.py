import hashlib, json, os, secrets, urllib.request, zipfile
from pathlib import Path
root = Path(__file__).resolve().parents[1]
runtime = root/'.runtime'
runtime.mkdir(exist_ok=True)
archive = runtime/'lrsql.zip'
if not archive.exists():
    urllib.request.urlretrieve('https://github.com/yetanalytics/lrsql/releases/download/v0.9.9/lrsql.zip',archive)
expected = json.loads((root/'release-assets.lock.json').read_text())['lrsql.zip']['sha256']
if hashlib.sha256(archive.read_bytes()).hexdigest() != expected:
    raise SystemExit('Release archive checksum mismatch; refusing to execute')
lrs = runtime/'lrs'
if not (lrs/'lrsql.jar').exists():
    with zipfile.ZipFile(archive) as z: z.extractall(lrs)
(lrs/'runtimes/linux/bin/java').chmod(0o755)
config = lrs/'config/lrsql.json'
if not config.exists():
    data = {'database':{'dbName':'portfolio-test'},'lrs':{'adminUserDefault':'local-admin','adminPassDefault':secrets.token_urlsafe(32),'apiKeyDefault':secrets.token_urlsafe(24),'apiSecretDefault':secrets.token_urlsafe(32),'authorityUrl':'http://localhost:8090'},'webserver':{'httpHost':'127.0.0.1','httpPort':8090,'sslPort':8490,'allowAllOrigins':False}}
    config.write_text(json.dumps(data,indent=2)); config.chmod(0o600)
print('Local LRS runtime ready. Credentials remain in ignored runtime configuration.')
