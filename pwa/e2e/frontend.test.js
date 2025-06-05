const { test, expect } = require('@playwright/test');

// Configure test timeout
test.setTimeout(30000);

// Base URL for the application
const BASE_URL = 'http://localhost:3000';

test.describe('TauTranslator Frontend Tests', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to the application before each test
    await page.goto(BASE_URL);
    // Wait for the page to be fully loaded
    await page.waitForLoadState('networkidle');
  });

  test('main index page loads correctly', async ({ page }) => {
    // Check if the title is present - handle multiple h1 elements
    const editorTitle = page.locator('h1.Editor_title__y1gd3');
    await expect(editorTitle).toHaveText('Tau Language Translator');
    
    // Check if both editor panels are present
    const panels = page.locator('[class*="editorPanel"]');
    await expect(panels).toHaveCount(2);
    
    // Check if language selectors are present
    const selectors = page.locator('[class*="languageSelector"]');
    await expect(selectors).toHaveCount(2);
    
    // Check if translate button is present
    await expect(page.locator('button:has-text("Translate")')).toBeVisible();
    
    // Check if swap button is present
    await expect(page.locator('[class*="swapButton"]')).toBeVisible();
    
    // Check if settings link is present
    await expect(page.locator('button:has-text("Settings")')).toBeVisible();
  });

  test('language swapping works correctly', async ({ page }) => {
    // Get initial language values
    const leftSelector = page.locator('[class*="languageSelector"]').first();
    const rightSelector = page.locator('[class*="languageSelector"]').last();
    
    // Set initial languages
    await leftSelector.selectOption('PLAIN_ENGLISH');
    await rightSelector.selectOption('TAU');
    
    // Enter some text in both panels
    const leftTextarea = page.locator('textarea').first();
    const rightTextarea = page.locator('textarea').last();
    
    await leftTextarea.fill('Test input in left panel');
    await rightTextarea.fill('Test input in right panel');
    
    // Click swap button
    await page.locator('[class*="swapButton"]').click();
    
    // Verify languages are swapped
    await expect(leftSelector).toHaveValue('TAU');
    await expect(rightSelector).toHaveValue('PLAIN_ENGLISH');
    
    // Verify text content is swapped
    await expect(leftTextarea).toHaveValue('Test input in right panel');
    await expect(rightTextarea).toHaveValue('Test input in left panel');
  });

  test('translation input/output works', async ({ page }) => {
    // Select languages
    const leftSelector = page.locator('[class*="languageSelector"]').first();
    const rightSelector = page.locator('[class*="languageSelector"]').last();
    
    await leftSelector.selectOption('PLAIN_ENGLISH');
    await rightSelector.selectOption('TAU');
    
    // Enter text to translate
    const leftTextarea = page.locator('textarea').first();
    await leftTextarea.fill('If x is greater than 5 then y equals 10');
    
    // Check that translate button is enabled
    const translateButton = page.locator('button:has-text("Translate")');
    await expect(translateButton).not.toBeDisabled();
    
    // Click translate button
    await translateButton.click();
    
    // Wait for translation to complete (button text changes back from "Translating...")
    await expect(translateButton).toHaveText('Translate', { timeout: 10000 });
    
    // Check that right panel has content (translation result)
    const rightTextarea = page.locator('textarea').last();
    const translationResult = await rightTextarea.inputValue();
    
    // Verify translation produced output
    expect(translationResult.length).toBeGreaterThan(0);
  });

  test('error display works correctly', async ({ page }) => {
    // Mock a failed API response
    await page.route('**/api/translate-unified', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ 
          success: false, 
          error: 'Test error message' 
        })
      });
    });
    
    // Enter text and try to translate
    const leftTextarea = page.locator('textarea').first();
    await leftTextarea.fill('Test input');
    
    const translateButton = page.locator('button:has-text("Translate")');
    await translateButton.click();
    
    // Check if error banner appears
    const errorBanner = page.locator('[class*="errorBanner"]');
    await expect(errorBanner).toBeVisible();
    
    // Check error message content
    const errorText = page.locator('[class*="errorText"]');
    await expect(errorText).toContainText('error');
    
    // Test closing the error
    const closeButton = page.locator('[class*="errorClose"]');
    await closeButton.click();
    
    // Verify error banner is hidden
    await expect(errorBanner).not.toBeVisible();
  });

  test('authentication modal shows and works', async ({ page }) => {
    // Check initial auth status
    const authStatus = page.locator('[class*="authStatus"]');
    await expect(authStatus).toContainText('Not Authenticated');
    
    // Click login button
    const loginButton = page.locator('button:has-text("Login")');
    await loginButton.click();
    
    // Check if modal appears
    const modal = page.locator('[class*="authModal"], [class*="modalOverlay"]').first();
    await expect(modal).toBeVisible();
    
    // Check modal has password input
    const passwordInput = page.locator('input[type="password"]');
    await expect(passwordInput).toBeVisible();
    
    // Check modal has submit button
    const submitButton = page.locator('[class*="authModal"] button:has-text("Authenticate"), [class*="modalContent"] button:has-text("Authenticate")');
    await expect(submitButton).toBeVisible();
    
    // Test closing modal
    const closeButton = page.locator('[class*="authModal"] [class*="closeButton"], [class*="modalHeader"] button').first();
    if (await closeButton.isVisible()) {
      await closeButton.click();
      await expect(modal).not.toBeVisible();
    } else {
      // Alternative: click outside modal
      await page.mouse.click(10, 10);
      await expect(modal).not.toBeVisible();
    }
  });

  test('translate button is disabled when input is empty', async ({ page }) => {
    // Clear any existing text
    const leftTextarea = page.locator('textarea').first();
    await leftTextarea.clear();
    
    // Check that translate button is disabled
    const translateButton = page.locator('button:has-text("Translate")');
    await expect(translateButton).toBeDisabled();
    
    // Add text
    await leftTextarea.fill('Some text');
    
    // Check that translate button is now enabled
    await expect(translateButton).not.toBeDisabled();
  });

  test('language selector options are correct', async ({ page }) => {
    const leftSelector = page.locator('[class*="languageSelector"]').first();
    
    // Click to open dropdown
    await leftSelector.click();
    
    // Check all expected options are present
    const expectedOptions = [
      'Plain English',
      'ILR (Intermediate Logic Representation)',
      'CNL (Controlled Natural Language)',
      'Tau Language Code'
    ];
    
    for (const optionText of expectedOptions) {
      const option = page.locator(`option:has-text("${optionText}")`);
      await expect(option).toBeVisible();
    }
  });

  test('settings page navigation works', async ({ page }) => {
    // Click settings button
    const settingsButton = page.locator('button:has-text("Settings")');
    await settingsButton.click();
    
    // Wait for navigation
    await page.waitForURL('**/settings');
    
    // Verify we're on settings page
    expect(page.url()).toContain('/settings');
  });

  test('textarea inputs are disabled during translation', async ({ page }) => {
    // Mock a slow API response
    let resolveTranslation;
    const translationPromise = new Promise(resolve => {
      resolveTranslation = resolve;
    });
    
    await page.route('**/api/translate-unified', async route => {
      await translationPromise;
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ 
          success: true, 
          translatedText: 'Translated result' 
        })
      });
    });
    
    // Enter text and start translation
    const leftTextarea = page.locator('textarea').first();
    const rightTextarea = page.locator('textarea').last();
    await leftTextarea.fill('Test input');
    
    const translateButton = page.locator('button:has-text("Translate")');
    await translateButton.click();
    
    // Check button shows "Translating..."
    await expect(translateButton).toHaveText('Translating...');
    
    // Check textareas are disabled
    await expect(leftTextarea).toBeDisabled();
    await expect(rightTextarea).toBeDisabled();
    
    // Complete the translation
    resolveTranslation();
    
    // Wait for translation to complete
    await expect(translateButton).toHaveText('Translate');
    
    // Check textareas are enabled again
    await expect(leftTextarea).not.toBeDisabled();
    await expect(rightTextarea).not.toBeDisabled();
  });
});