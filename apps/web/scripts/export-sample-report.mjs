import {chromium} from '@playwright/test';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../..');
const browser=await chromium.launch({channel:process.env.PLAYWRIGHT_CHANNEL??'msedge',headless:true});
try {
 const page=await browser.newPage();
 const base=process.env.SAT_SA_WEB_URL??'http://127.0.0.1:3001';
 await page.goto(base);
 await page.getByRole('button',{name:'Assess CSE-01'}).waitFor({timeout:60000});
 const runs=(await (await page.request.get(base+'/api/service/analytics/runs?limit=100')).json()).items;
 const selected=runs.find(run=>run.dataset_id==='demo');
 if(!selected)throw new Error('Completed default synthetic run required');
 await page.getByLabel('Assessment run').selectOption(selected.run_id);
 await page.getByRole('button',{name:'Report',exact:true}).click();
 await page.getByRole('heading',{name:'Review indicators and source references'}).waitFor();
 await page.pdf({path:path.join(root,'docs/submission/sample-supervisory-report.pdf'),format:'A4',printBackground:true});
} finally {await browser.close();}
