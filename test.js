const c = require('./calc.js'), a = require('assert');
a(Math.abs(c.rer(4) - 197.99) < 0.05);
a(Math.abs(c.mer(4, 'neutered') - 237.6) < 0.1);
const d = c.portions(240, { kcal_cup: 400, kcal_kg: 3800 }); a(Math.abs(d.cups - 0.6) < 1e-9); a(Math.abs(d.grams - 63.2) < 0.1);
const w = c.portions(197, { kcal_can: 197, kcal_kg: 1263 }); a.equal(w.cans, 1); a(Math.abs(w.grams - 156) < 0.1);
const s = c.split(240, { kcal_cup: 400 }, { kcal_can: 80 }, 0.5); a(Math.abs(s.cups - 0.3) < 1e-9); a(Math.abs(s.cans - 1.5) < 1e-9);
console.log('ok');
