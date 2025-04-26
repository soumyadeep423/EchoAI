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

function generateAudio() {
    const text = document.getElementById("textInput").value;
    const voicePreset = document.getElementById("voicePreset").value;
    const button = document.querySelector("button");
    const audioPlayer = document.getElementById("audioPlayer");
    const generationTime = document.getElementById("generationTime");
  
    if (!text.trim()) {
      alert("Please enter some text!");
      return;
    }
  
    button.disabled = true;
    button.innerText = "Generating...";
    generationTime.innerText = "";  // Clear previous time
  
    const startTime = performance.now();  // Start timing
  
    fetch("/api/generate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        text: text,
        voice_preset: voicePreset
      })
    })
    .then(response => {
      if (!response.ok) {
        throw new Error("Failed to generate audio");
      }
      return response.blob();
    })
    .then(blob => {
      const endTime = performance.now();  // End timing
      const elapsedTime = ((endTime - startTime) / 1000).toFixed(2);  // in seconds
  
      const audioURL = URL.createObjectURL(blob);
      audioPlayer.src = audioURL;
      audioPlayer.style.display = "block";
      audioPlayer.play();
  
      generationTime.innerText = `Generated in ${elapsedTime} seconds.`;
    })
    .catch(error => {
      console.error(error);
      alert("An error occurred while generating audio.");
    })
    .finally(() => {
      button.disabled = false;
      button.innerText = "Generate";
    });
  }

  function addEmotionTag() {
    const emotionSelect = document.getElementById("emotionSelect");
    const textInput = document.getElementById("textInput");
    const emotion = emotionSelect.value;
  
    let tag = "";
  
    if (emotion === "happy") {
      tag = "[laughter]";
    } else if (emotion === "sad") {
      tag = "[sighs]";
    } else if (emotion === "angry") {
      tag = "[clears throat]";
    } else {
      // Neutral - no tag needed
      return;
    }
  
    // Insert the tag at the current cursor position
    const cursorPos = textInput.selectionStart;
    const textBefore = textInput.value.substring(0, cursorPos);
    const textAfter = textInput.value.substring(cursorPos);
    textInput.value = textBefore + " " + tag + " " + textAfter;
  
    // Reset selection back
    textInput.selectionStart = textInput.selectionEnd = cursorPos + tag.length + 2;
  
    // Reset emotion selection to default
    emotionSelect.selectedIndex = 0;
  }
  
  