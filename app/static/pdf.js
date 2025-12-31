let currentFile = null;
let extractedText = '';

// DOM Elements
const dropArea = document.getElementById('dropArea');
const fileInput = document.getElementById('fileInput');
const processBtn = document.getElementById('processBtn');
const progressSection = document.getElementById('progressSection');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const textOutput = document.getElementById('textOutput');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const fileStatus = document.getElementById('fileStatus');
const stats = document.getElementById('stats');
const charCount = document.getElementById('charCount');
const wordCount = document.getElementById('wordCount');
const pagesPreview = document.getElementById('pagesPreview');
const pagesContainer = document.getElementById('pagesContainer');

// Event Listeners
fileInput.addEventListener('change', handleFileSelect);
dropArea.addEventListener('dragover', handleDragOver);
dropArea.addEventListener('dragleave', handleDragLeave);
dropArea.addEventListener('drop', handleDrop);

function handleFileSelect(e) {
    const file = e.target.files[0];
    handleFile(file);
}

function handleDragOver(e) {
    e.preventDefault();
    dropArea.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    dropArea.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    dropArea.classList.remove('drag-over');
    
    const file = e.dataTransfer.files[0];
    handleFile(file);
}

function handleFile(file) {
    if (!file) return;
    
    // Check file type
    const validTypes = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg'];
    if (!validTypes.includes(file.type)) {
        showToast('Please upload a PDF or image file', 'error');
        return;
    }
    
    // Check file size (16MB)
    if (file.size > 16 * 1024 * 1024) {
        showToast('File size must be less than 16MB', 'error');
        return;
    }
    
    currentFile = file;
    
    // Update UI
    fileName.textContent = file.name;
    fileStatus.textContent = 'Ready for processing';
    fileStatus.className = 'status-success';
    fileInfo.style.display = 'block';
    
    // Enable process button
    processBtn.disabled = false;
    processBtn.classList.remove('disabled');
    
    showToast(`File "${file.name}" loaded successfully`, 'success');
}

async function processFile() {
    if (!currentFile) {
        showToast('Please select a file first', 'error');
        return;
    }
    
    // Show progress
    progressSection.style.display = 'block';
    progressFill.style.width = '30%';
    progressText.textContent = 'Uploading file...';
    processBtn.disabled = true;
    processBtn.classList.add('processing');
    
    const formData = new FormData();
    formData.append('file', currentFile);
    
    // Get processing options
    const preprocess = document.getElementById('preprocess').checked;
    const language = document.getElementById('language').value;
    
    // Use advanced processing endpoint with options
    formData.append('preprocess', preprocess);
    formData.append('language', language);
    
    try {
        progressFill.style.width = '60%';
        progressText.textContent = 'Processing with OCR...';
        
        const response = await fetch('/process_options', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            progressFill.style.width = '100%';
            progressText.textContent = 'Processing complete!';
            
            extractedText = data.extracted_text;
            
            // Update text output
            textOutput.value = extractedText;
            
            // Update stats
            charCount.textContent = data.char_count.toLocaleString();
            wordCount.textContent = data.word_count.toLocaleString();
            stats.style.display = 'flex';
            
            // Update status
            fileStatus.textContent = 'Processing complete';
             
                // === PAGE-BY-PAGE PREVIEW FEATURE ===
                // Displays a concise preview of the first 200 characters from each page
                const pagesContainer = document.getElementById('pagesContainer');
                pagesContainer.innerHTML = '';  
                
                data.pages.forEach((text, i) => {
                    const div = document.createElement('div');
                    div.className = 'page-item';
                    div.innerHTML = `
                        <h5>Page ${i+1} <i class="fas fa-file"></i></h5>
                        <p class="page-preview">${text.substring(0, 200).trim()}...</p>
                    `;
                    pagesContainer.appendChild(div);
                });
                
                document.getElementById('pagesPreview').style.display = 'block';

                // === END OF PAGE-BY-PAGE PREVIEW FEATURE ===

            showToast('Text extracted successfully!', 'success');
            
            // Hide progress after delay
            setTimeout(() => {
                progressSection.style.display = 'none';
                progressFill.style.width = '0%';
            }, 2000);
            
        } else {
            throw new Error(data.error || 'Processing failed');
        }
        
    } catch (error) {
        console.error('Error:', error);
        progressText.textContent = 'Processing failed';
        fileStatus.textContent = 'Processing failed';
        fileStatus.className = 'status-error';
        showToast(`Error: ${error.message}`, 'error');
    } finally {
        processBtn.disabled = false;
        processBtn.classList.remove('processing');
    }
}

function copyText() {
    if (!extractedText) {
        showToast('No text to copy', 'error');
        return;
    }
    
    navigator.clipboard.writeText(extractedText)
        .then(() => showToast('Text copied to clipboard!', 'success'))
        .catch(err => showToast('Failed to copy text', 'error'));
}

async function downloadText() {
    if (!extractedText) {
        showToast('No text to download', 'error');
        return;
    }
    
    const blob = new Blob([extractedText], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    
    a.href = url;
    a.download = `extracted_text_${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    
    showToast('Text downloaded successfully!', 'success');
}

function clearAll() {
    currentFile = null;
    extractedText = '';
    
    // Reset UI
    fileInput.value = '';
    textOutput.value = '';
    fileInfo.style.display = 'none';
    stats.style.display = 'none';
    pagesPreview.style.display = 'none';
    progressSection.style.display = 'none';
    progressFill.style.width = '0%';
    pagesContainer.innerHTML = '';
    
    processBtn.disabled = false;
    
    showToast('All cleared', 'info');
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    
    // Set type-based styling
    switch(type) {
        case 'success':
            toast.style.background = '#28a745';
            break;
        case 'error':
            toast.style.background = '#dc3545';
            break;
        case 'info':
            toast.style.background = '#17a2b8';
            break;
    }
    
    toast.textContent = message;
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Check for Tesseract availability
    fetch('/')
        .then(response => {
            if (!response.ok) throw new Error('Server not responding');
        })
        .catch(error => {
            showToast('Please ensure the Flask server is running', 'error');
        });
});