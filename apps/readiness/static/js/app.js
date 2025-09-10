# (Save the following to static/js/app.js)
"""
(function(){
const ip = window.__IPRRS__;
const af = window.__AFAQ__;
if (Array.isArray(ip)) {
const ctx = document.getElementById('iprrsChart');
if (ctx) {
new Chart(ctx, {
type: 'radar',
data: {
labels: ['1','2','3','4','5','6'],
datasets: [{ label: 'I‑PRRS', data: ip }]
},
options: { scales: { r: { beginAtZero: true, suggestedMax: 10 } } }
});
}
}
if (Array.isArray(af)) {
const ctx2 = document.getElementById('afaqChart');
if (ctx2) {
new Chart(ctx2, {
type: 'bar',
data: {
labels: ['1','2','3','4','5','6','7','8','9','10'],
datasets: [{ label: 'AFAQ', data: af }]
},
options: { scales: { y: { beginAtZero: true, suggestedMax: 5 } } }
});
}
}
})();

