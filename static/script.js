document.addEventListener("DOMContentLoaded", () => {
    const words = ["Authentic", "Expressive", "Natural"];
    const colors = ["#9b51e0", "#A4F4FF", "#2EFFC0"]; // Existing + new colors
    let wordIndex = 0;
    let typingText = document.querySelector(".typing-text");

    function typeEffect(word) {
        typingText.style.color = colors[wordIndex]; // Change color before typing
        let i = 0;
        let interval = setInterval(() => {
            typingText.textContent = word.substring(0, i + 1);
            i++;
            if (i === word.length) {
                setTimeout(() => eraseEffect(word), 1000);
                clearInterval(interval);
            }
        }, 150);
    }

    function eraseEffect(word) {
        let i = word.length;
        let interval = setInterval(() => {
            typingText.textContent = word.substring(0, i - 1);
            i--;
            if (i === 0) {
                wordIndex = (wordIndex + 1) % words.length;
                setTimeout(() => typeEffect(words[wordIndex]), 500);
                clearInterval(interval);
            }
        }, 100);
    }

    // Start Animation
    typeEffect(words[wordIndex]);
});