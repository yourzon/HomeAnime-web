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
// Function to update table changes for visual
function updateTable(){
   // Find the header row to dynamically determine column positions
   const headers = document.querySelectorAll("#mangaTable thead th");

   // Initialize variables for chapter and is_releas columns
   let chapterIndex = -1;
   let releaseIndex = -1;

   // Loop through the headers and match them by text content (case-insensitive)
   headers.forEach((header, index) => {
       const headerText = header.innerText.trim().toLowerCase();
       if (headerText === "chapter read") {
           chapterIndex = index; // Save the index for the "Chapter" column
       } else if (headerText === "up to date") {
           releaseIndex = index; // Save the index for the "is_latest" column
       }
   });
   
    // Get all rows in the table body
    const rows = document.querySelectorAll("#mangaTable tbody tr");
    rows.forEach(row => {
            // Handle rounding of the dynamic 'chapter' column
            let chapterCell = row.cells[chapterIndex];
            let chapterValue = parseFloat(chapterCell.innerText);
            if (chapterValue % 1 === 0) {
                chapterCell.innerText = parseInt(chapterValue);
            } else {
                chapterCell.innerText = chapterValue;
            }

            // Handle conversion of the dynamic 'is_releas' column
            const releaseCell = row.cells[releaseIndex];
            if (releaseCell.textContent.trim() === '1') {
                releaseCell.textContent = 'True';
            } else if (releaseCell.textContent.trim() === '0') {
                releaseCell.textContent = 'false';
            }
        });
}
// Function to handle redirection
function redirectToDetails(mangaId) {
    // Redirect to the Flask route with the manga ID as a parameter
    window.location.href = `/manga/${mangaId}`;
    
}
window.onload = function() {
    updateTable();
}
