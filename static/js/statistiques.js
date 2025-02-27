document.addEventListener('DOMContentLoaded', function () {        
    const statusRead = JSON.parse(document.getElementById('status-read-data').textContent);
    const yearRelease = JSON.parse(document.getElementById('year-release-data').textContent);
    const tagsStats = JSON.parse(document.getElementById('tags-stats-data').textContent);

    function populateTable(tableId, data) {
        const table = document.getElementById(tableId);
        const tbody = table.getElementsByTagName('tbody')[0];
        tbody.innerHTML = '';
        data.forEach(rowData => {
            const row = document.createElement('tr');
            rowData.forEach(cellData => {
                const cell = document.createElement('td');
                cell.textContent = cellData;
                row.appendChild(cell);
            });
            tbody.appendChild(row);
        });
    }

    populateTable('status-read', statusRead);
    populateTable('year-table', yearRelease);
    populateTable('tags-table', tagsStats);
});
