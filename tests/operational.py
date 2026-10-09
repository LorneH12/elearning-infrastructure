"""Real SQL LRS + real browser course smoke test. Not a conformance suite."""
import base64, json, os, subprocess, time, uuid, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / '.runtime/lrs'
REPORT = ROOT / 'reports'
REPORT.mkdir(exist_ok=True)
config = json.loads((RUNTIME/'config/lrsql.json').read_text())
creds = config['lrs']
auth = 'Basic ' + base64.b64encode((creds['apiKeyDefault']+':'+creds['apiSecretDefault']).encode()).decode()
headers = {'Authorization': auth, 'X-Experience-API-Version': '1.0.3', 'Content-Type': 'application/json'}
results = []
def request(path, method='GET', body=None, authorized=True, base='http://127.0.0.1:8090', extra=None):
    hs = dict(headers) if authorized else {'X-Experience-API-Version':'1.0.3'}
    hs.update(extra or {})
    req = urllib.request.Request(base+path, data=None if body is None else json.dumps(body).encode(), headers=hs, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as res: return res.status, res.read()
    except urllib.error.HTTPError as e: return e.code, e.read()
def check(name, predicate):
    results.append({'test':name,'status':'passed' if predicate else 'failed'})
    if not predicate: raise AssertionError(name)
def wait(port, process):
    for _ in range(60):
        if process.poll() is not None: raise RuntimeError('Service exited; inspect local runtime log')
        try:
            urllib.request.urlopen(f'http://127.0.0.1:{port}/',timeout=1)
            return
        except urllib.error.HTTPError: return
        except OSError: time.sleep(0.5)
    raise TimeoutError(f'Service on {port} did not become ready')
def start_lrs(log):
    process = subprocess.Popen([str(RUNTIME/'runtimes/linux/bin/java'),'-Dfile.encoding=UTF-8','-server','-cp','lrsql.jar','lrsql.sqlite.main'],cwd=RUNTIME,stdout=log,stderr=log)
    wait(8090,process)
    return process
lrs = gateway = None
try:
    with (ROOT/'.runtime/lrs-test.log').open('w') as log:
        lrs = start_lrs(log)
        check('LRS rejects unauthenticated statement reads', request('/xapi/statements',authorized=False)[0] == 401)
        sid = str(uuid.uuid4())
        statement = {'id':sid,'actor':{'mbox':'mailto:synthetic-test@example.org'},'verb':{'id':'http://adlnet.gov/expapi/verbs/completed'},'object':{'id':'https://example.org/portfolio-test/operational'},'result':{'completion':True}}
        route = '/xapi/statements?statementId='+sid
        check('LRS stores valid completion',request(route,'PUT',statement)[0] == 204)
        check('LRS retrieves exact statement ID',json.loads(request(route)[1])['id'] == sid)
        check('Identical retry is idempotent',request(route,'PUT',statement)[0] == 204)
        changed = dict(statement, object={'id':'https://example.org/changed'})
        check('Conflicting duplicate rejected',request(route,'PUT',changed)[0] == 409)
        check('Malformed statement rejected',request('/xapi/statements','POST',{'invalid':True})[0] == 400)
        lrs.terminate(); lrs.wait(timeout=20)
        lrs = start_lrs(log)
        check('Statement persists after LRS restart',json.loads(request(route)[1])['id'] == sid)
        env = dict(os.environ,LRS_KEY=creds['apiKeyDefault'],LRS_SECRET=creds['apiSecretDefault'])
        gateway = subprocess.Popen(['node','gateway/server.mjs'],cwd=ROOT,env=env,stdout=log,stderr=log)
        wait(8088,gateway)
        check('Gateway rejects unauthenticated writes',request('/api/events','POST',{},False,'http://127.0.0.1:8088')[0] == 401)
        check('Gateway rejects foreign origin',request('/api/session','POST',{},False,'http://127.0.0.1:8088',{'Origin':'https://untrusted.example'})[0] == 403)
        browser = subprocess.run(['node','tests/player.cjs'],cwd=ROOT,capture_output=True,text=True,timeout=90)
        if browser.returncode:
            (REPORT/'browser-error.txt').write_text(browser.stderr)
        check('Browser launches Adapt and opens lesson',browser.returncode == 0)
        evidence=json.loads(browser.stdout.strip().splitlines()[-1])
        for receipt in evidence['receipts']:
            got = json.loads(request('/xapi/statements?statementId='+receipt['id'])[1])
            check('Browser event retrievable: '+receipt['verb'],got['id'] == receipt['id'])
        (REPORT/'browser-results.json').write_text(json.dumps(evidence,indent=2)+'\n')
finally:
    for process in (gateway,lrs):
        if process and process.poll() is None:
            process.terminate()
            try: process.wait(timeout=20)
            except subprocess.TimeoutExpired: process.kill(); process.wait()
    (REPORT/'operational-results.json').write_text(json.dumps({'tests':results,'scope':'Local operational smoke test; Moodle and visual authoring not tested'},indent=2)+'\n')
    print(json.dumps(results,indent=2))
