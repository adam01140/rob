function editPDF() {
        if (!uploadedPdfFile) {
            alert('No PDF file is loaded for editing.');
            return;
        }
        var formData = new FormData();
        formData.append('pdf', uploadedPdfFile);
        var inputs = document.querySelectorAll('#questions input, #fieldList input');
        
		// Add this in your JavaScript when preparing data to send to the server
var inputs = document.querySelectorAll('#questions input, #fieldList input');
inputs.forEach(input => {
    if (input.type === 'checkbox') {
        formData.append(input.id, input.checked ? 'Yes' : 'No');
    } else {
        formData.append(input.id, input.value);
    }
});




		
        fetch('/edit_pdf', {
            method: 'POST',
            body: formData,
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.blob();
        })
        .then(blob => {
            var url = window.URL.createObjectURL(blob);
            document.getElementById('pdfFrame').src = url;
            document.getElementById('pdfPreview').style.display = 'block';
        })
        .catch(error => {
            console.error('Error updating PDF:', error);
            alert('Error updating PDF: ' + error.message);
        });
    }