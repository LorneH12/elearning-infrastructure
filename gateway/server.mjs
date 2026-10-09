import http from 'node:http';
import { readFile } from 'node:fs/promises';
import { resolve, extname, sep } from 'node:path';
import { randomUUID, randomBytes } from 'node:crypto';

const port = Number(process.env.PORT || 8088);
const root = resolve(process.env.COURSE_ROOT || 'dist/web');
const endpoint = process.env.LRS_ENDPOINT || 'http://127.0.0.1:8090/xapi';
if (!process.env.LRS_KEY || !process.env.LRS_SECRET) throw new Error('LRS credentials required');
const authorization = 'Basic ' + Buffer.from(`${process.env.LRS_KEY}:${process.env.LRS_SECRET}`).toString('base64');
const sessions = new Map();
const types = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.woff': 'font/woff', '.woff2': 'font/woff2', '.mp4': 'video/mp4', '.vtt': 'text/vtt' };
function json(res, status, body) {
  res.writeHead(status, { 'Content-Type': 'application/json', 'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff' });
  res.end(JSON.stringify(body));
}
const server = http.createServer(async (req, res) => {
  try {
    const url = new URL(req.url, `http://localhost:${port}`);
    // Loopback demo only. Production requires authenticated LMS launch and identity binding.
    if (![`localhost:${port}`, `127.0.0.1:${port}`].includes(req.headers.host)) return json(res, 403, { error: 'Host rejected' });
    if (req.headers.origin && ![`http://localhost:${port}`, `http://127.0.0.1:${port}`].includes(req.headers.origin)) return json(res, 403, { error: 'Origin rejected' });
    if (req.method === 'POST' && url.pathname === '/api/session') {
      for (const [token, session] of sessions) if (session.expires < Date.now()) sessions.delete(token);
      if (sessions.size >= 100) return json(res, 429, { error: 'Session capacity reached' });
      const token = randomBytes(32).toString('hex');
      sessions.set(token, { id: randomUUID(), expires: Date.now() + 3600000, count: 0 });
      return json(res, 201, { token });
    }
    if (req.method === 'POST' && url.pathname === '/api/events') {
      const session = sessions.get(req.headers['x-session-token']);
      if (!session || session.expires < Date.now()) return json(res, 401, { error: 'Session required' });
      if (++session.count > 200) return json(res, 429, { error: 'Test event limit reached' });
      let body = '';
      for await (const chunk of req) {
        body += chunk;
        if (body.length > 4096) return json(res, 413, { error: 'Too large' });
      }
      let event;
      try { event = JSON.parse(body); } catch { return json(res, 400, { error: 'Invalid JSON' }); }
      if (!/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(event.id || '') || !['initialized','experienced','completed'].includes(event.verb) || !/^(course|co-\d+)$/.test(event.activity || '')) return json(res, 400, { error: 'Invalid event' });
      const statement = {
        id: event.id,
        actor: { objectType: 'Agent', account: { homePage: 'https://example.org/portfolio-test', name: session.id } },
        verb: { id: `http://adlnet.gov/expapi/verbs/${event.verb}`, display: { 'en-US': event.verb } },
        object: { objectType: 'Activity', id: `https://example.org/portfolio-test/${event.activity}` },
        context: { registration: session.id }
      };
      if (event.verb === 'completed') statement.result = { completion: true };
      const upstream = await fetch(`${endpoint}/statements?statementId=${event.id}`, {
        method: 'PUT', headers: { Authorization: authorization, 'X-Experience-API-Version': '1.0.3', 'Content-Type': 'application/json' },
        body: JSON.stringify(statement), signal: AbortSignal.timeout(10000)
      });
      if (!upstream.ok) return json(res, 502, { error: 'LRS rejected event' });
      return json(res, 200, { id: event.id, stored: true });
    }
    if (req.method !== 'GET') return json(res, 405, { error: 'Method not allowed' });
    const file = resolve(root, '.' + decodeURIComponent(url.pathname === '/' ? '/index.html' : url.pathname));
    if (!file.startsWith(root + sep)) return json(res, 403, { error: 'Path rejected' });
    try {
      const body = await readFile(file);
      res.writeHead(200, { 'Content-Type': types[extname(file)] || 'application/octet-stream', 'X-Content-Type-Options': 'nosniff' });
      res.end(body);
    } catch { json(res, 404, { error: 'Not found' }); }
  } catch { json(res, 502, { error: 'Service unavailable' }); }
});
server.listen(port, '127.0.0.1', () => console.log(`Local test player: http://127.0.0.1:${port}`));
