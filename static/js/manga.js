function roundChapter() {
    // Get the single <p> element with class 'chapter'
    let chapterElement = document.querySelector("p.chapter");

    if (chapterElement) {
        // Extract only the chapter number (assuming format "Chapter: X", where X is a number)
        let chapterText = chapterElement.innerText.trim();
        let chapterValue = parseFloat(chapterText.replace(/^Chapter:\s*/, '').trim()); // Remove "Chapter: " part and trim

        if (!isNaN(chapterValue)) {  // Ensure the value is a valid number
            let chapterText = "Chapter: ";  // Keep the Chapter part fixed
            if (chapterValue % 1 === 0) {
                // If it has no fractional part (e.g., 1050.0), convert it to an integer
                chapterElement.innerHTML = `<strong>${chapterText}</strong>${parseInt(chapterValue)}`;  // Convert to integer
            } else {
                // If it has a fractional part (e.g., 1050.5), leave it as a float
                chapterElement.innerHTML = `<strong>${chapterText}</strong>${chapterValue}`;  // Keep as float
            }
        }
    }
}
window.onload = function() {
    roundChapter();  // Round the chapter values when the page loads
}
