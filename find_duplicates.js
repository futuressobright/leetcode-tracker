const fs = require('fs');

// Read the CSS file
const css = fs.readFileSync('static/css/style.css', 'utf8');

// Simple regex to find CSS selectors
const selectorRegex = /([.#][^{\n]+)\s*{/g;
const selectors = {};

let match;
while ((match = selectorRegex.exec(css)) !== null) {
    const selector = match[1].trim();
    selectors[selector] = (selectors[selector] || 0) + 1;
}

// Print duplicates
console.log('Duplicate selectors found:');
Object.entries(selectors)
    .filter(([_, count]) => count > 1)
    .sort(([_, a], [__, b]) => b - a)
    .forEach(([selector, count]) => {
        console.log(`${selector}: ${count} times`);
    });
