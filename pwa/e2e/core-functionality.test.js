const { test, expect } = require('@playwright/test');

// Configure test timeout
test.setTimeout(30000);

// Base URL for the application
const BASE_URL = 'http://localhost:3000';

test.describe('TauTranslator Core Functionality', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to the application before each test
    await page.goto(BASE_URL);
    // Wait for the page to be fully loaded
    await page.waitForLoadState('networkidle');
  });

  test('✅ Page loads with essential UI elements', async ({ page }) => {
    // Check title
    await expect(page.locator('h1').last()).toContainText('Tau Language Translator');
    
    // Check editor panels exist
    const panels = page.locator('[class*="textarea"]');
    await expect(panels).toHaveCount(2);
    
    // Check controls exist
    await expect(page.locator('button:has-text("Translate")')).toBeVisible();
    await expect(page.locator('[title="Swap Languages"]')).toBeVisible();
  });

  test('✅ Language selection and swapping', async ({ page }) => {
    // Get language selectors
    const selectors = page.locator('select');
    const leftSelector = selectors.first();
    const rightSelector = selectors.last();
    
    // Set specific languages
    await leftSelector.selectOption('PLAIN_ENGLISH');
    await rightSelector.selectOption('TAU');
    
    // Add content to panels
    const textareas = page.locator('textarea');
    const leftTextarea = textareas.first();
    const rightTextarea = textareas.last();
    
    await leftTextarea.fill('Hello from left');
    await rightTextarea.fill('Hello from right');
    
    // Click swap
    await page.locator('[title="Swap Languages"]').click();
    
    // Verify swap worked
    await expect(leftSelector).toHaveValue('TAU');
    await expect(rightSelector).toHaveValue('PLAIN_ENGLISH');
    await expect(leftTextarea).toHaveValue('Hello from right');
    await expect(rightTextarea).toHaveValue('Hello from left');
  });

  test('✅ Translation functionality', async ({ page }) => {
    // Setup languages
    const selectors = page.locator('select');
    await selectors.first().selectOption('PLAIN_ENGLISH');
    await selectors.last().selectOption('TAU');
    
    // Enter text
    const leftTextarea = page.locator('textarea').first();
    await leftTextarea.fill('x is greater than 5');
    
    // Translate
    const translateButton = page.locator('button:has-text("Translate")');
    await expect(translateButton).toBeEnabled();
    
    // Mock successful response
    await page.route('**/api/translate-unified', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ 
          success: true, 
          translatedText: 'x > 5' 
        })
      });
    });
    
    await translateButton.click();
    
    // Check result
    const rightTextarea = page.locator('textarea').last();
    await expect(rightTextarea).toHaveValue('x > 5');
  });

  test('✅ Authentication status display', async ({ page }) => {
    // Check auth status area exists
    const authStatus = page.locator('[class*="authStatus"]');
    await expect(authStatus).toBeVisible();
    
    // Check for auth indicator
    const authText = await authStatus.textContent();
    expect(authText).toMatch(/Authenticated|Not Authenticated/);
  });

  test('✅ Settings navigation', async ({ page }) => {
    // Find and click settings
    const settingsButton = page.locator('button:has-text("Settings")');
    await expect(settingsButton).toBeVisible();
    
    await settingsButton.click();
    
    // Verify navigation
    await page.waitForURL('**/settings');
    expect(page.url()).toContain('/settings');
  });
});

test.describe('TauTranslator Error Handling', () => {
  
  test('✅ Empty input validation', async ({ page }) => {
    await page.goto(BASE_URL);
    
    // Ensure textarea is empty
    const leftTextarea = page.locator('textarea').first();
    await leftTextarea.clear();
    
    // Check translate button is disabled
    const translateButton = page.locator('button:has-text("Translate")');
    await expect(translateButton).toBeDisabled();
    
    // Add text and verify enabled
    await leftTextarea.fill('test');
    await expect(translateButton).toBeEnabled();
  });

  test('✅ API error handling', async ({ page }) => {
    await page.goto(BASE_URL);
    
    // Mock error response
    await page.route('**/api/translate-unified', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ 
          success: false, 
          error: 'Translation service unavailable' 
        })
      });
    });
    
    // Try to translate
    await page.locator('textarea').first().fill('test');
    await page.locator('button:has-text("Translate")').click();
    
    // Wait for any error indication (could be banner, alert, or in textarea)
    await page.waitForTimeout(1000);
    
    // Check page still functional
    const translateButton = page.locator('button:has-text("Translate")');
    await expect(translateButton).toBeVisible();
  });
});