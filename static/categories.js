// Генеруємо стабільний колір на основі тексту (назви категорії)
function stableColorFromText(text) {
    let hash = 0;
    for (let i = 0; i < text.length; i++) {
        hash = text.charCodeAt(i) + ((hash << 5) - hash);
    }
    const hue = Math.abs(hash) % 360;
    const saturation = 60 + (Math.abs(hash) % 20); // 60–80%
    const lightness = 40 + (Math.abs(hash) % 15); // 40–55%
    return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
}

// Застосовуємо колір до всіх категорій
document.querySelectorAll('.category').forEach(el => {
    const name = el.dataset.category;
    el.style.backgroundColor = stableColorFromText(name);
});