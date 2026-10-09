const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const page = await browser.newPage({ reducedMotion: 'reduce' });
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.addInitScript(() => {
    window.recorded = [];
    window.addEventListener('portfolio:recorded', e => window.recorded.push(e.detail));
  });
  try {
    await page.goto('http://127.0.0.1:8088/', { waitUntil: 'domcontentloaded' });
    await page.waitForFunction(() => window.recorded.some(x => x.verb === 'initialized'));
    await page.getByRole('link', { name: 'View Presentation Components. Item 1 of 3.', exact: true }).click();
    await page.waitForFunction(() => window.recorded.some(x => x.verb === 'experienced'));
    await page.locator('.component__inner').first().waitFor({ state: 'visible' });
    await page.screenshot({ path: 'reports/player-desktop.png', fullPage: false, animations: 'disabled' });
    const receipts = await page.evaluate(() => window.recorded);
    if (errors.length) throw new Error(errors.join('\n'));
    console.log(JSON.stringify({ status: 'passed', receipts, errors }));
  } catch (error) {
    await page.screenshot({ path: 'reports/player-error.png' }).catch(() => {});
    require('node:fs').writeFileSync('reports/player-error.html', await page.content());
    console.error(JSON.stringify({ errors, buttons: await page.getByRole('button').allTextContents() }));
    throw error;
  } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exit(1); });
