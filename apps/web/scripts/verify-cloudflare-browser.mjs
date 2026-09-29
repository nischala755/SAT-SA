import {chromium} from '@playwright/test';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const origin=process.argv[2];
if(!origin||!origin.startsWith('https://'))throw new Error('Pass the Cloudflare HTTPS origin');
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../..');
const values=(await fs.readFile(path.join(root,'.env.cloudflare.local'),'utf8')).split(/\r?\n/);
const line=values.find(item=>item.startsWith('SAT_SA_AUTH_TOKENS='));
if(!line)throw new Error('Local Cloudflare demo identity missing');
const token=Object.keys(JSON.parse(line.slice('SAT_SA_AUTH_TOKENS='.length)))[0];
const browser=await chromium.launch({channel:process.env.PLAYWRIGHT_CHANNEL??'msedge',headless:true});
try {
 const page=await browser.newPage();
 await page.goto(origin,{waitUntil:'domcontentloaded'});
 await page.getByText('Backend connected').waitFor({timeout:30000});
 await page.getByLabel('Bearer token').fill(token);
 await page.getByRole('button',{name:'Assess CSE-01'}).waitFor({timeout:30000});
 console.log(JSON.stringify({origin,frontend_loaded:true,backend_connected:true,authenticated_evidence_visible:true}));
} finally {await browser.close();}
