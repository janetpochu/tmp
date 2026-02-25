---
name: playwright-advanced-planner
tools: Glob, Grep, Read, Write, Bash
skills:
  - e2e
  - playwright-skill  # Add this!
---

## Phase 1: Navigate, Explore & Capture

1. Use playwright-skill to run custom script:
```javascript
   const { chromium } = require('playwright');
   
   const apiResponses = {};
   
   const browser = await chromium.launch({ headless: false });
   const context = await browser.newContext({
     recordHar: {
       path: '__mocks__/api/captured.har',
       mode: 'full',
       urlFilter: '**/api/**'
     }
   });
   
   // OR capture programmatically:
   page.on('response', async response => {
     if (response.url().includes('/api/')) {
       const endpoint = new URL(response.url()).pathname;
       const data = await response.json();
       apiResponses[endpoint] = data;
     }
   });
   
   // Navigate and explore
   await page.goto('https://example.com');
   await page.click('button[data-test="submit"]');
   
   // Save mocks
   fs.writeFileSync(
     '__mocks__/api/responses.json',
     JSON.stringify(apiResponses, null, 2)
   );
```
