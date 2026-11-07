import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const framesDir = path.resolve(__dirname, '../../docs/frames');
if (fs.existsSync(framesDir)) {
  fs.rmSync(framesDir, { recursive: true, force: true });
}
fs.mkdirSync(framesDir, { recursive: true });

async function run() {
  console.log('🚀 Launching Chromium for mobile demo recording...');
  const browser = await chromium.launch({
    headless: true,
  });

  const context = await browser.newContext({
    viewport: { width: 390, height: 750 },
    deviceScaleFactor: 2,
    isMobile: true,
    hasTouch: true,
  });

  const page = await context.newPage();
  let frameCount = 0;

  async function captureFrame(delayMs = 120, repeat = 1) {
    if (delayMs > 0) await page.waitForTimeout(delayMs);
    const framePath = path.join(framesDir, `frame_${String(frameCount++).padStart(4, '0')}.png`);
    await page.screenshot({ path: framePath });
    for (let r = 1; r < repeat; r++) {
      const copyPath = path.join(framesDir, `frame_${String(frameCount++).padStart(4, '0')}.png`);
      fs.copyFileSync(framePath, copyPath);
    }
  }

  // 1. Visit Domains Page
  console.log('📱 1. Loading Domains view...');
  await page.goto('http://localhost:8085/', { waitUntil: 'networkidle' });
  await captureFrame(400, 3); // Hold on domains list

  // Scroll slightly down to showcase domains
  await page.mouse.wheel(0, 150);
  await captureFrame(250, 2);

  // 2. Click on the first domain card or navigate directly to demo deck
  console.log('🃏 2. Navigating to CardSwipe / Scenario Deck...');
  await page.goto('http://localhost:8085/criar/dating', { waitUntil: 'networkidle' });

  await page.waitForTimeout(500);
  await captureFrame(300, 4); // Hold on initial scenario card

  // 3. Scroll down slightly on the card to see the context and dilemma
  console.log('👀 3. Examining scenario & game theory question...');
  await page.mouse.wheel(0, 100);
  await captureFrame(200, 2);

  // 4. Reveal / Flip Card
  console.log('🔄 4. Flipping card to reveal Game Theory analysis...');
  const revealBtn = page.locator('button:has-text("Revelar"), button:has-text("Resposta"), button:has-text("Ver"), button:has-text("Gabarito"), button:has-text("Mostrar")').first();
  if (await revealBtn.count() > 0) {
    await revealBtn.click();
  } else {
    // Click on the card body to flip
    const cardBody = page.locator('div[style*="perspective"], .cursor-pointer').first();
    if (await cardBody.count() > 0) {
      await cardBody.click();
    }
  }

  await captureFrame(300, 5); // Hold on revealed explanation and payoff

  // Scroll inside explanation
  await page.mouse.wheel(0, 120);
  await captureFrame(200, 2);

  // 5. Swipe / Next card
  console.log('➡️ 5. Navigating to next scenario...');
  const nextBtn = page.locator('button:has-text("Próximo"), button:has-text("Next"), button:has-text("Avançar"), button:has-text("Errado"), button:has-text("Certo")').first();
  if (await nextBtn.count() > 0) {
    await nextBtn.click();
    await captureFrame(300, 4);
  }

  console.log(`✅ Recording complete! Captured ${frameCount} frames.`);
  await browser.close();
}

run().catch(err => {
  console.error('❌ Error recording demo:', err);
  process.exit(1);
});
