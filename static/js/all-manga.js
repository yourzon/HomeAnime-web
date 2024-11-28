// Function to filter table rows based on the search input
function searchTable() {
    let input = document.getElementById('searchInput'); // Get search input element
    let filter = input.value.toLowerCase(); // Convert input to lowercase for case-insensitive comparison
    let table = document.getElementById('mangaTable'); // Get the table
    let rows = table.getElementsByTagName('tr'); // Get all table rows

    // Loop through all table rows (skip the first row as it is the header)
    for (let i = 1; i < rows.length; i++) {
        let cells = rows[i].getElementsByTagName('td');
        let rowText = '';

        // Loop through each cell in the row
        for (let j = 0; j < cells.length; j++) {
            rowText += cells[j].textContent.toLowerCase(); // Concatenate the cell text
        }

        // If the row text contains the filter value, display the row; otherwise, hide it
        if (rowText.includes(filter)) {
            rows[i].style.display = '';
        } else {
            rows[i].style.display = 'none';
        }
    }
}
function roundChapterColumn() {
    // Get all rows in the table
    let rows = document.querySelectorAll("#mangaTable tbody tr");
    
    // Loop through each row and round the 'chapter' value (index 2)
    rows.forEach(row => {
        let chapterCell = row.cells[2];  // Get the cell for the chapter (index 2)
        let chapterValue = parseFloat(chapterCell.innerText);  // Convert the chapter value to a number
    // Check if the value has a fractional part
    if (chapterValue % 1 === 0) {
        // If it has no fractional part (e.g., 1050.0), convert it to an integer
        chapterCell.innerText = parseInt(chapterValue);  // Convert to integer
    } else {
        // If it has a fractional part (e.g., 1050.5), leave it as a float
        chapterCell.innerText = chapterValue;  // Keep as float
    }
    });
}
// Function to handle redirection
function redirectToDetails(mangaId) {
    // Redirect to the Flask route with the manga ID as a parameter
    window.location.href = `/manga/${mangaId}`;
    
}
window.onload = function() {
    roundChapterColumn();  // Round the chapter values when the page loads
}
