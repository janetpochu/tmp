// .claude/skills/e2e/templates/capture-mocks.js
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

async function captureMocks(url) {
  const mocks = {};
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  page.on('response', async response => {
    if (response.url().includes('/api/')) {
      const endpoint = new URL(response.url()).pathname
        .replace(/^\/api\//, '')
        .replace(/\//g, '-');
      
      try {
        const data = await response.json();
        mocks[endpoint] = {
          status: response.status(),
          data: data,
          headers: response.headers()
        };
      } catch (e) {
        // Not JSON
      }
    }
  });
  
  await page.goto(url);
  // ... perform interactions ...
  
  // Save mocks
  for (const [endpoint, mock] of Object.entries(mocks)) {
    fs.writeFileSync(
      path.join('__mocks__/api', `${endpoint}.json`),
      JSON.stringify(mock, null, 2)
    );
  }
  
  await browser.close();
}
