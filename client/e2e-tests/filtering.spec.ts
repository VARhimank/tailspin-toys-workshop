import { test, expect } from '@playwright/test';

test.describe('Game filtering', () => {
  test('should filter by publisher and category, then clear filters', async ({ page }) => {
    let initialGameCount = 0;
    let firstPublisher = '';
    let firstCategory = '';

    await test.step('Navigate to home page and wait for catalog', async () => {
      await page.goto('/');
      await expect(page.getByTestId('games-grid')).toBeVisible();
      await expect(page.getByTestId('publisher-filter')).toBeVisible();
      await expect(page.getByTestId('category-filter')).toBeVisible();
    });

    await test.step('Capture baseline card count and first game badges', async () => {
      const gameCards = page.getByTestId('game-card');
      initialGameCount = await gameCards.count();
      expect(initialGameCount).toBeGreaterThan(0);

      firstPublisher = (await gameCards.first().getByTestId('game-publisher').innerText()).trim();
      firstCategory = (await gameCards.first().getByTestId('game-category').innerText()).trim();
    });

    await test.step('Filter by publisher', async () => {
      await page.getByTestId('publisher-filter').selectOption({ label: firstPublisher });
      const publisherCount = await page.getByTestId('game-card').count();
      expect(publisherCount).toBeGreaterThan(0);
      for (let index = 0; index < publisherCount; index += 1) {
        await expect(page.getByTestId('game-card').nth(index).getByTestId('game-publisher')).toHaveText(firstPublisher);
      }
    });

    await test.step('Apply category filter in combination (AND)', async () => {
      await page.getByTestId('category-filter').selectOption({ label: firstCategory });
      const combinedCount = await page.getByTestId('game-card').count();
      expect(combinedCount).toBeGreaterThan(0);
      for (let index = 0; index < combinedCount; index += 1) {
        await expect(page.getByTestId('game-card').nth(index).getByTestId('game-publisher')).toHaveText(firstPublisher);
        await expect(page.getByTestId('game-card').nth(index).getByTestId('game-category')).toHaveText(firstCategory);
      }
    });

    await test.step('Clear filters and restore full game list', async () => {
      await page.getByTestId('clear-filters-button').click();
      await expect(page.getByTestId('publisher-filter')).toHaveValue('all');
      await expect(page.getByTestId('category-filter')).toHaveValue('all');
      await expect(page.getByTestId('game-card')).toHaveCount(initialGameCount);
    });
  });

  test('should show no-results state when selected filters match no games', async ({ page }) => {
    await test.step('Navigate to home page and wait for controls', async () => {
      await page.goto('/');
      await expect(page.getByTestId('publisher-filter')).toBeVisible();
      await expect(page.getByTestId('category-filter')).toBeVisible();
    });

    await test.step('Apply a no-match category value and verify empty filtered state', async () => {
      await page.evaluate(() => {
        const categorySelect = document.querySelector('[data-testid="category-filter"]') as HTMLSelectElement | null;
        if (!categorySelect) return;

        const noMatchOption = document.createElement('option');
        noMatchOption.value = '999999';
        noMatchOption.text = 'No Match Category';
        categorySelect.appendChild(noMatchOption);
      });

      await page.getByTestId('category-filter').selectOption('999999');
      await expect(page.getByText('No games match the selected filters.')).toBeVisible();
      await expect(page.getByTestId('game-card')).toHaveCount(0);
    });
  });
});
