import { expect, test } from '@playwright/test';

test('real overview to evidence to human review and audit', async ({page}) => {
  await page.goto('/');
  await expect(page.getByRole('heading',{name:'Supervisory overview'})).toBeVisible();
  await expect(page.getByRole('button',{name:'Assess CSE-01'})).toBeVisible({timeout:60000});
  await page.getByRole('button',{name:'Assess CSE-01'}).click();
  await expect(page.getByRole('heading',{name:'Entity assessment: CSE-01'})).toBeVisible();
  await page.getByRole('button',{name:'Inspect High-severity alerts closed unusually quickly'}).click();
  await expect(page.getByRole('heading',{name:'Evidence and supervisory hypothesis'})).toBeVisible();
  await page.getByRole('button',{name:/Open source/}).first().click();
  await expect(page.getByText('Source record', {exact:true})).toBeVisible();
  await page.getByLabel('Supervisory note').fill('Browser verification: synthetic evidence checked; further contextual review required.');
  await page.getByLabel('Review outcome').selectOption('further_investigation');
  await page.getByRole('button',{name:'Record human decision'}).click();
  await expect(page.getByText('Human decision recorded in audit trail.')).toBeVisible();
  await page.getByRole('button',{name:'Close evidence'}).click();
  await page.getByRole('button',{name:'Audit trail',exact:true}).click();
  await expect(page.getByText('review_recorded').first()).toBeVisible();
});

test('queue opens its selected source and all signal evidence is pageable',async({page})=>{
  await page.goto('/');
  await expect(page.getByRole('button',{name:'Assess CSE-01'})).toBeVisible({timeout:60000});
  await page.getByRole('button',{name:'Review queue',exact:true}).click();
  await expect(page.getByRole('button',{name:'Review evidence'}).first()).toBeVisible();
  await page.getByRole('button',{name:'Next page',exact:true}).click();
  const sample=(await (await page.request.get('/api/service/review-queue?offset=25&limit=1')).json()).items[0];
  await page.getByRole('button',{name:'Review evidence'}).first().click();
  await expect(page.getByText('Source record',{exact:true})).toBeVisible();
  await expect(page.getByText('Source record',{exact:true}).locator('..')).toContainText(sample.record_id);
  await expect(page.getByRole('button',{name:'Next evidence page'})).toBeVisible();
});

test('CSV/JSON wizard previews and imports an immutable submission',async({page})=>{
  const response=await page.request.get('/api/service/evidence?dataset_id=demo&cse_id=CSE-01&table=cses');
  const cse=(await response.json()).items[0];
  await page.goto('/');
  await expect(page.getByRole('button',{name:'Assess CSE-01'})).toBeVisible({timeout:60000});
  await page.getByRole('button',{name:'Data ingestion',exact:true}).click();
  await page.getByLabel('Dataset version').fill('browser-'+Date.now());
  await page.getByLabel('Structured files').setInputFiles({name:'cses.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify([cse]))});
  await page.getByRole('button',{name:'Validate and preview'}).click();
  await expect(page.getByText(/Valid: true/)).toBeVisible();
  await page.getByRole('button',{name:'Import immutable dataset'}).click();
  await expect(page.getByText('ingestion job: completed',{exact:false})).toBeVisible({timeout:15000});
});
