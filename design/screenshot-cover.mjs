import { chromium } from "playwright";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

(async () => {
  const html = path.resolve(__dirname, "cover-render.html");
  const out = path.resolve(__dirname, "cover-todayflow.png");
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1200 } });
  await page.goto(`file://${html}`, { waitUntil: "networkidle" });
  await page.locator("#cover").screenshot({ path: out });
  await browser.close();
  console.log("Wrote", out);
})();
