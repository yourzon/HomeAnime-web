// Function to filter table rows based on the search input
function searchTable() {
    const input = document.getElementById('searchInput'); // Cache search input element
    const filter = input.value.toLowerCase(); // Convert input to lowercase for case-insensitive comparison
    const table = document.getElementById('mangaTable'); // Cache the table element
    const rows = table.getElementsByTagName('tr'); // Cache all table rows

    // Loop through all table rows (skip the first row as it is the header)
    for (let i = 1; i < rows.length; i++) {
        const cells = rows[i].getElementsByTagName('td');
        let rowTextFound = false;

        // Loop through each cell in the row
        for (let j = 0; j < cells.length; j++) {
            const cellText = cells[j].textContent.toLowerCase();
            // Check if the cell contains the filter text
            if (cellText.includes(filter)) {
                rowTextFound = true;
                break; // No need to check further cells
            }
        }

        // Show or hide the row based on whether a match was found
        rows[i].style.display = rowTextFound ? '' : 'none';
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
