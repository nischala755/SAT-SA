import {chromium} from '@playwright/test';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import fs from 'node:fs/promises';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../..');
const output=path.join(root,'docs/submission');
const browser=await chromium.launch({channel:process.env.PLAYWRIGHT_CHANNEL??'msedge',headless:true});
const context=await browser.newContext({viewport:{width:1280,height:720},recordVideo:{dir:output,size:{width:1280,height:720}}});
const page=await context.newPage();
const pause=ms=>page.waitForTimeout(ms);
try {
 const base=process.env.SAT_SA_WEB_URL??'http://127.0.0.1:3001';
 await page.goto(base);
 await page.getByRole('button',{name:'Assess CSE-01'}).waitFor({timeout:60000});
 const response=await page.request.get(base+'/api/service/analytics/runs?limit=100');
 const runs=(await response.json()).items;
 const current=runs.find(r=>r.dataset_id==='demo');
 const prior=runs.find(r=>r.dataset_id==='demo-2024');
 if(!current||!prior)throw new Error('Record the walkthrough after creating and analysing both demo periods');
 await page.getByLabel('Assessment run').selectOption(current.run_id);
 await page.getByRole('heading',{name:'Supervisory overview'}).scrollIntoViewIfNeeded();await pause(4000);
 await page.getByRole('button',{name:'Assess CSE-01'}).click();await pause(4000);
 await page.getByRole('button',{name:'Inspect High-severity alerts closed unusually quickly'}).click();await pause(5000);
 await page.getByRole('button',{name:/Open source/}).first().click();await pause(4000);
 await page.getByRole('button',{name:'Close evidence'}).click();
 await page.getByRole('button',{name:'Negative space',exact:true}).click();
 await page.getByLabel('CSE filter').fill('');
 await page.getByRole('heading',{name:'Negative space'}).waitFor();await page.evaluate(()=>window.scrollBy(0,630));await pause(5000);
 await page.getByRole('button',{name:'Period comparison',exact:true}).click();
 await page.getByLabel('Earlier run').selectOption(prior.run_id);
 await page.getByRole('button',{name:'Compare periods'}).click();
 await page.getByText('Descriptive evidence change',{exact:false}).first().waitFor();await page.evaluate(()=>window.scrollBy(0,540));await pause(6000);
 await page.getByRole('button',{name:'Report',exact:true}).click();
 await page.getByRole('heading',{name:'Review indicators and source references'}).waitFor();await page.evaluate(()=>window.scrollBy(0,550));await pause(5000);
 await page.getByRole('button',{name:'Validation',exact:true}).click();await pause(5000);
 await page.getByRole('button',{name:'Audit trail',exact:true}).click();await pause(4000);
} finally {
 const video=page.video();
 await context.close();await browser.close();
 if(video){const source=await video.path();await fs.rename(source,path.join(output,'demo-walkthrough.webm'));}
}
