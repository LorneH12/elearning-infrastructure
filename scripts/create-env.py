from pathlib import Path
import secrets
p = Path(__file__).resolve().parents[1]/'.env'
if p.exists(): raise SystemExit('Existing .env left unchanged')
p.write_text('\n'.join(f'{key}={secrets.token_urlsafe(32)}' for key in ['LRS_KEY','LRS_SECRET','LRS_ADMIN_PASSWORD','MOODLE_DB_PASSWORD','MOODLE_ADMIN_PASSWORD'])+'\n')
p.chmod(0o600)
print('Created local credentials in ignored .env; no credentials printed.')
