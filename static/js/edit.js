document.addEventListener('DOMContentLoaded', function () {
    const dropdown = document.getElementById('dropdown');
    const inputField = document.getElementById('inputFields');

    dropdown.addEventListener('change', function () {
        const selectedValue = dropdown.value;

        // Show the input and submit button when a valid option is selected
        if (selectedValue) {
            inputField.style.display = 'block';
        } else {
            inputField.style.display = 'none';
        }
    });
});