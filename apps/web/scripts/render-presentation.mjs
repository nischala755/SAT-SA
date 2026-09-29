import {chromium} from '@playwright/test';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../..');
const browser=await chromium.launch({channel:process.env.PLAYWRIGHT_CHANNEL??'msedge',headless:true});
try {
 const page=await browser.newPage();
 await page.goto('file:///'+path.join(root,'docs/submission/technical-presentation.html').replaceAll('\\','/'));
 await page.pdf({path:path.join(root,'docs/submission/technical-presentation.pdf'),printBackground:true,preferCSSPageSize:true});
} finally {await browser.close();}
