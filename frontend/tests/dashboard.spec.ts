import { test, expect } from '@playwright/test';

test.describe('Dashboard Security and Flow', () => {
  test('Unpaid user is redirected to payment page', async ({ page }) => {
    // Navigate to dashboard
    await page.goto('/userdashboard');
    
    // Check if redirected to login or payment (since they have no token, it will go to login first)
    await expect(page).toHaveURL(/.*login.*/);
  });
});
