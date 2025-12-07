document.addEventListener('DOMContentLoaded', function () {
    // Initialize all upload areas
    const uploadAreas = document.querySelectorAll('.upload-area');

    uploadAreas.forEach(area => {
        const input = area.querySelector('input[type="file"]');
        const card = area.closest('.doc-upload-card');

        // Handle click (delegated to label automatically, but we add visual feedback)
        area.addEventListener('click', () => {
            // input.click(); // Not needed as label handles it
        });

        // Handle file selection
        input.addEventListener('change', function (e) {
            handleFiles(this.files, card, area);
        });

        // Handle drag and drop
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            area.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        ['dragenter', 'dragover'].forEach(eventName => {
            area.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            area.addEventListener(eventName, unhighlight, false);
        });

        function highlight(e) {
            area.classList.add('highlight');
            card.classList.add('drag-active');
        }

        function unhighlight(e) {
            area.classList.remove('highlight');
            card.classList.remove('drag-active');
        }

        area.addEventListener('drop', handleDrop, false);

        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;

            // Update the input files
            input.files = files;
            handleFiles(files, card, area);
        }
    });

    function handleFiles(files, card, area) {
        if (files.length > 0) {
            const file = files[0];
            showFilePreview(file, card, area);
        }
    }

    function showFilePreview(file, card, area) {
        // Create preview HTML
        const fileSize = formatBytes(file.size);
        const fileName = file.name;

        // Hide upload area content (but keep the input!)
        // We'll replace the visual content of the label

        const originalContent = area.innerHTML;
        // Store original content if we want to revert (optional)

        // Check if we already have a preview
        const existingPreview = area.querySelector('.uploaded-file-preview');
        if (existingPreview) {
            existingPreview.remove();
        }

        // Hide the default upload placeholder elements
        const placeholderElements = area.querySelectorAll('svg, .upload-text, .upload-hint');
        placeholderElements.forEach(el => el.style.display = 'none');

        // Create new preview element
        const previewHtml = `
            <div class="uploaded-file-preview" style="display: flex; align-items: center; gap: 12px; width: 100%;">
                <div class="file-icon" style="width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; background: #10b981; border-radius: 8px; color: white;">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6zm-1 2l5 5h-5V4zM6 20V4h6v6h6v10H6z" />
                    </svg>
                </div>
                <div class="file-details" style="flex: 1; text-align: left;">
                    <div class="file-name" style="font-weight: 600; color: #1f2937;">${fileName}</div>
                    <div class="file-size" style="font-size: 12px; color: #6b7280;">${fileSize}</div>
                </div>
                <div class="change-btn" style="color: #667eea; font-size: 13px; font-weight: 600;">Change</div>
            </div>
        `;

        area.insertAdjacentHTML('beforeend', previewHtml);
        card.classList.add('uploaded');
    }

    function formatBytes(bytes, decimals = 2) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }
});
