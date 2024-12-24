document.addEventListener('DOMContentLoaded', () => {
    const dropdown = document.getElementById('categoryDropdown');

    // Fetch dropdown options from the server
    fetch('/get-options')
        .then(response => response.json())
        .then(options => {
            // Populate dropdown with options
            options.forEach(option => {
                const newOption = document.createElement('option');
                newOption.value = option.value;
                newOption.textContent = option.label;
                dropdown.appendChild(newOption);
            });
        })
        .catch(error => console.error('Error fetching options:', error));
});


function handleSelection() {
    const dropdown = document.getElementById("categoryDropdown");
    const selectedValue = dropdown.value;

    if (selectedValue) {
        fetch(`/process-selection`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ selection: selectedValue })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Response:', data);
            // alert(`Server response: ${data.message}`);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
    const heading = document.getElementById('heading');

    if (selectedValue) {
        heading.textContent = `Create 4 groups of 4 in ${selectedValue.toUpperCase()}`;
    } else {
        heading.textContent = 'Create 4 groups of 4!';
    }    
}
