// tools/compare-pdfjs.mjs
import fs from "node:fs/promises";
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);

const pdfjsLib = require("pdfjs-dist/legacy/build/pdf.js");

async function extract(pdfPath) {
    const data = new Uint8Array(await fs.readFile(pdfPath));
    const doc = await pdfjsLib.getDocument({ data }).promise;
    const pages = [];
    for (let i = 1; i <= doc.numPages; i++) {
        const page = await doc.getPage(i);
        const content = await page.getTextContent();
        // Grouper par ligne (y) puis par x
        const items = content.items.filter(x => x.str && x.str.trim());
        const lines = [];
        items.forEach(x => {
            const y = x.transform[5];
            let line = lines.find(l => Math.abs(l.y - y) < 3);
            if (!line) {
                line = { y, items: [] };
                lines.push(line);
            }
            line.items.push({ str: x.str, x: x.transform[4] });
        });
        lines.sort((a, b) => b.y - a.y);
        const text = lines.map(l => {
            l.items.sort((a, b) => a.x - b.x);
            return l.items.map(i => i.str).join("");
        }).join("\n");
        pages.push(text);
    }
    return pages;
}

const results = {};
for (let n = 1; n <= 12; n++) {
    const path = `themes/T${n}.pdf`;
    try {
        results[n] = await extract(path);
        console.log(`T${n} : ${results[n].length} pages`);
    } catch (e) {
        console.error(`T${n} : ${e.message}`);
    }
}

await fs.writeFile("tools/out/pdfjs-text.json", JSON.stringify(results, null, 2));
console.log("✅ tools/out/pdfjs-text.json");
