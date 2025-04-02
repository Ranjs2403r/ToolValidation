document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('upload-form');
    const fileInputs = document.querySelectorAll('input[type="file"]');
    const uploadButton = document.getElementById('upload-button');
    const loadingSpinner = document.getElementById('loading-spinner');
    const errorAlert = document.getElementById('error-alert');
    const errorText = document.getElementById('error-text');
    
    // Update file input labels when files are selected
    fileInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const fileName = e.target.files[0]?.name || 'Choose file';
            const label = document.querySelector(`label[for="${e.target.id}"]`);
            if (label) {
                // Keep "Choose" text but replace file name
                const chooseText = label.querySelector('.choose-text');
                const fileNameElement = label.querySelector('.file-name');
                
                if (fileNameElement) {
                    fileNameElement.textContent = fileName;
                } else if (e.target.files[0]) {
                    // Create file name element if it doesn't exist
                    const span = document.createElement('span');
                    span.className = 'file-name';
                    span.textContent = fileName;
                    label.appendChild(span);
                }
                
                // Add the "selected" class to style the label
                if (e.target.files[0]) {
                    label.classList.add('file-selected');
                } else {
                    label.classList.remove('file-selected');
                }
            }
            
            // Enable upload button if both files are selected
            checkEnableUploadButton();
        });
    });
    
    function checkEnableUploadButton() {
        const dataFile = document.getElementById('data-file').files[0];
        const rulesFile = document.getElementById('rules-file').files[0];
        
        if (dataFile && rulesFile) {
            uploadButton.disabled = false;
        } else {
            uploadButton.disabled = true;
        }
    }
    
    // Handle form submission
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Show loading spinner and hide any previous error
        loadingSpinner.classList.remove('d-none');
        errorAlert.classList.add('d-none');
        uploadButton.disabled = true;
        
        const formData = new FormData(uploadForm);
        
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'An error occurred during file upload');
                });
            }
            return response.text();
        })
        .then(html => {
            // Replace the current page with the results page
            document.open();
            document.write(html);
            document.close();
        })
        .catch(error => {
            // Display error message
            errorText.textContent = error.message;
            errorAlert.classList.remove('d-none');
            
            // Hide loading spinner and re-enable upload button
            loadingSpinner.classList.add('d-none');
            checkEnableUploadButton();
        });
    });
    
    // Reset error when alert is closed
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('btn-close') && e.target.closest('.alert')) {
            e.target.closest('.alert').classList.add('d-none');
        }
    });
});
