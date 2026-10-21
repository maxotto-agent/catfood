// Energy maths for cats. RER and factors: Merck Veterinary Manual, "Daily maintenance energy requirements for dogs and cats".
const FACTORS = {
  neutered: ['Neutered adult', 1.2],
  intact: ['Intact adult', 1.4],
  inactive: ['Obesity-prone', 1.0],
  kitten: ['Kitten', 2.5],
};
function rer(kg) { return 70 * Math.pow(kg, 0.75); }
function mer(kg, stage) { return rer(kg) * FACTORS[stage][1]; }
// Dry food: cups. Wet food: cans (grams per can derived from kcal per can and kcal per kg).
function portions(kcal, food) {
  const grams = food.kcal_kg ? kcal / food.kcal_kg * 1000 : null;
  return food.kcal_can ? { cans: kcal / food.kcal_can, grams } : { cups: kcal / food.kcal_cup, grams };
}
// Split the daily calories between dry and wet: wetShare of kcal from cans.
function split(kcal, dry, wet, wetShare) {
  return { cups: kcal * (1 - wetShare) / dry.kcal_cup, cans: kcal * wetShare / wet.kcal_can };
}
// Cups of the new food that match the calories of the old amount.
function switchCups(oldCups, oldKcalCup, newKcalCup) {
  const kcal = oldCups * oldKcalCup;
  return { kcal, cups: kcal / newKcalCup, change: newKcalCup / oldKcalCup - 1 };
}
// 7-day mix, each day's total equals `kcal`. Share of new food per day.
const MIX = [0.25, 0.25, 0.5, 0.5, 0.75, 0.75, 1];
function mixPlan(kcal, oldKcalCup, newKcalCup) {
  return MIX.map((s, i) => ({ day: i + 1, share: s, newCups: kcal * s / newKcalCup, oldCups: kcal * (1 - s) / oldKcalCup }));
}
const FRACS = ['', '1/8', '1/4', '3/8', '1/2', '5/8', '3/4', '7/8'];
function fmtCups(c) {
  const eighths = Math.round(c * 8), w = Math.floor(eighths / 8), f = FRACS[eighths % 8];
  if (!w && !f) return '0';
  return (w ? w : '') + (w && f ? ' ' : '') + f;
}
if (typeof module !== 'undefined') module.exports = { split, FACTORS, rer, mer, portions, switchCups, mixPlan, fmtCups };
