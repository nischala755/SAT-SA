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
