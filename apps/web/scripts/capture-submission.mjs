import {chromium} from '@playwright/test';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../..');
const browser=await chromium.launch({channel:process.env.PLAYWRIGHT_CHANNEL??'msedge',headless:true});
try {
 const page=await browser.newPage({viewport:{width:1440,height:900},deviceScaleFactor:1});
 await page.goto(process.env.SAT_SA_WEB_URL??'http://127.0.0.1:3001');
 await page.getByRole('button',{name:'Assess CSE-01'}).waitFor({timeout:60000});
 await page.getByRole('button',{name:'Negative space',exact:true}).click();
 await page.getByText('Expected critical-asset activity absent').waitFor();
 await page.getByRole('heading',{name:'Negative space'}).scrollIntoViewIfNeeded();
 await page.evaluate(()=>window.scrollBy(0,650));
 await page.screenshot({path:path.join(root,'docs/submission/negative-space.png')});
 await page.getByRole('button',{name:'Report',exact:true}).click();
 await page.getByRole('heading',{name:'Review indicators and source references'}).waitFor();
 await page.getByRole('heading',{name:'Supervisory assessment report'}).scrollIntoViewIfNeeded();
 await page.evaluate(()=>window.scrollBy(0,260));
 await page.screenshot({path:path.join(root,'docs/submission/report-view.png')});
} finally {await browser.close();}
