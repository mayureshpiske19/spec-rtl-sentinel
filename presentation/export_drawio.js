// Renders a .drawio file to PNG using draw.io's own rendering engine
// (app.diagrams.net) via Playwright's bundled Chromium, by screenshotting the
// rendered diagram canvas. Produces a clean, draw.io-accurate PNG.
//
// Usage: node export_drawio.js <input.drawio> <output.png>
const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

(async () => {
  const input = process.argv[2] || path.join("..", "docs", "architecture.drawio");
  const output = process.argv[3] || path.join("..", "docs", "architecture.png");
  const xml = fs.readFileSync(input, "utf8");

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ deviceScaleFactor: 3 });
  await page.goto("https://app.diagrams.net/?splash=0&mode=device", {
    waitUntil: "domcontentloaded",
  });
  await page.waitForTimeout(6000);

  // Open Extras -> Edit Diagram, paste XML, Apply.
  await page.getByText("Extras", { exact: true }).click();
  await page.waitForTimeout(600);
  await page.getByText("Edit Diagram...", { exact: true }).click();
  await page.waitForTimeout(600);
  await page.locator("textarea").first().evaluate((el, val) => {
    const setter = Object.getOwnPropertyDescriptor(
      window.HTMLTextAreaElement.prototype, "value").set;
    setter.call(el, val);
    el.dispatchEvent(new Event("input", { bubbles: true }));
  }, xml);
  await page.getByRole("button", { name: "Apply" }).click();
  await page.waitForTimeout(1500);

  // Turn off the background grid so the export is clean white.
  await page.evaluate(() => {
    try {
      if (window.editorUi) {
        window.editorUi.editor.graph.setGridEnabled(false);
        window.editorUi.editor.graph.view.validateBackground();
      }
    } catch (e) {}
  });
  await page.waitForTimeout(500);

  // Turn the grid off via the View menu for a clean white background.
  try {
    await page.getByText("View", { exact: true }).click();
    await page.waitForTimeout(400);
    await page.getByText("Grid", { exact: true }).first().click();
    await page.waitForTimeout(400);
  } catch (e) { await page.keyboard.press("Escape"); }

  // Hide the side panels so the canvas has maximum room, and remove the grid
  // (it is a CSS background image on the canvas) for a clean white export.
  await page.addStyleTag({ content: `
    .geSidebarContainer, .geFormatContainer, .mxWindow,
    .geToolbarContainer { display:none !important; }
    .geDiagramContainer { left:0 !important; right:0 !important; width:100% !important;
      background-image:none !important; }
    .geDiagramContainer svg { background-image:none !important; }
  `});
  await page.evaluate(() => {
    document.querySelectorAll(".geDiagramContainer").forEach(c => {
      c.style.backgroundImage = "none";
      const svg = c.querySelector("svg");
      if (svg) svg.style.backgroundImage = "none";
    });
  });
  await page.waitForTimeout(400);

  // Fit the diagram to the view, then screenshot the canvas element.
  await page.keyboard.press("Control+Shift+H");
  await page.waitForTimeout(1000);
  const cont = await page.$(".geDiagramContainer");
  await cont.screenshot({ path: output });
  console.log("wrote", output);
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
