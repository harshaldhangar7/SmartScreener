// Smart Resume Screener - Enhanced JavaScript with Modern Features
class SmartScreener {
    constructor() {
        this.init();
        this.setupEventListeners();
        this.initializeAnimations();
    }

    init() {
        // Enable tooltips everywhere
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        this.tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
        
        // Auto dismiss alerts after 5 seconds
        setTimeout(() => {
            const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
            alerts.forEach(alert => {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            });
        }, 5000);

        // Initialize drag and drop
        this.initDragAndDrop();
        
        // Initialize progress animations
        this.animateProgressBars();
        
        // Initialize stats counters
        this.animateCounters();
    }

    setupEventListeners() {
        // File input handling
        const resumeInput = document.getElementById('resume');
        if (resumeInput) {
            resumeInput.addEventListener('change', (e) => this.handleFileSelect(e));
        }

        // Search functionality
        const searchInput = document.getElementById('candidateSearch');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.filterCandidates(e.target.value));
        }

        // Model switching
        const modelSwitcher = document.getElementById('modelSwitcher');
        if (modelSwitcher) {
            modelSwitcher.addEventListener('change', (e) => this.switchModel(e.target.value));
        }

        // Real-time updates
        this.setupRealTimeUpdates();
    }

    initializeAnimations() {
        // Animate cards on scroll
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fadeInUp');
                }
            });
        }, { threshold: 0.1 });

        document.querySelectorAll('.candidate-card, .stats-card, .glass-card').forEach(card => {
            observer.observe(card);
        });
    }

    initDragAndDrop() {
        const uploadArea = document.querySelector('.upload-area') || document.querySelector('#resume')?.parentElement;
        if (!uploadArea) return;

        // Make the entire upload area a drop zone
        uploadArea.classList.add('upload-area');
        
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, this.preventDefaults, false);
            document.body.addEventListener(eventName, this.preventDefaults, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => uploadArea.classList.add('dragover'), false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => uploadArea.classList.remove('dragover'), false);
        });

        uploadArea.addEventListener('drop', (e) => this.handleDrop(e), false);

        // Add visual feedback
        const dropText = document.createElement('div');
        dropText.className = 'drop-text';
        dropText.innerHTML = `
            <i class="bi bi-cloud-upload" style="font-size: 3rem; color: var(--neon-blue);"></i>
            <h4>Drag & Drop Resume Here</h4>
            <p>or click to browse files</p>
            <small>Supports PDF, DOC, and DOCX files</small>
        `;
        
        if (!uploadArea.querySelector('.drop-text')) {
            uploadArea.appendChild(dropText);
        }
    }

    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            const resumeInput = document.getElementById('resume');
            if (resumeInput) {
                resumeInput.files = files;
                this.handleFileSelect({ target: { files: files } });
            }
        }
    }

    handleFileSelect(e) {
        const file = e.target.files[0];
        if (!file) return;

        // Validate file type
        const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword'];
        if (!allowedTypes.includes(file.type)) {
            this.showNotification('Please select a PDF, DOC, or DOCX file.', 'error');
            return;
        }

        // Validate file size (10MB limit)
        if (file.size > 10 * 1024 * 1024) {
            this.showNotification('File size must be less than 10MB.', 'error');
            return;
        }

        // Show file preview
        this.showFilePreview(file);
        
        // Show upload progress
        this.showUploadProgress();
    }

    showFilePreview(file) {
        const previewContainer = document.getElementById('filePreview') || this.createFilePreview();
        
        previewContainer.innerHTML = `
            <div class="glass-card p-3 mt-3">
                <div class="d-flex align-items-center">
                    <i class="bi bi-file-earmark-text me-3" style="font-size: 2rem; color: var(--neon-blue);"></i>
                    <div class="flex-grow-1">
                        <h6 class="mb-1">${file.name}</h6>
                        <small class="text-muted">${this.formatFileSize(file.size)} • ${file.type.split('/')[1].toUpperCase()}</small>
                    </div>
                    <div class="ai-indicator" title="AI Analysis Ready"></div>
                </div>
            </div>
        `;
    }

    createFilePreview() {
        const container = document.createElement('div');
        container.id = 'filePreview';
        const uploadArea = document.querySelector('.upload-area') || document.querySelector('#resume')?.parentElement;
        if (uploadArea) {
            uploadArea.appendChild(container);
        }
        return container;
    }

    showUploadProgress() {
        const progressContainer = document.getElementById('uploadProgress') || this.createProgressContainer();
        
        progressContainer.innerHTML = `
            <div class="glass-card p-3 mt-3">
                <div class="d-flex align-items-center mb-2">
                    <div class="loading-spinner me-3"></div>
                    <span>Processing resume with AI analysis...</span>
                </div>
                <div class="progress-modern">
                    <div class="progress-bar" role="progressbar" style="width: 0%"></div>
                </div>
            </div>
        `;

        // Simulate progress
        this.animateProgress(progressContainer.querySelector('.progress-bar'));
    }

    createProgressContainer() {
        const container = document.createElement('div');
        container.id = 'uploadProgress';
        const uploadArea = document.querySelector('.upload-area') || document.querySelector('#resume')?.parentElement;
        if (uploadArea) {
            uploadArea.appendChild(container);
        }
        return container;
    }

    animateProgress(progressBar) {
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress >= 100) {
                progress = 100;
                clearInterval(interval);
            }
            progressBar.style.width = progress + '%';
        }, 200);
    }

    animateProgressBars() {
        const progressBars = document.querySelectorAll('.progress-bar');
        progressBars.forEach(bar => {
            const width = bar.style.width || bar.getAttribute('aria-valuenow') + '%';
            bar.style.width = '0%';
            setTimeout(() => {
                bar.style.transition = 'width 1.5s ease-in-out';
                bar.style.width = width;
            }, 100);
        });
    }

    animateCounters() {
        const counters = document.querySelectorAll('.stats-number');
        counters.forEach(counter => {
            const target = parseInt(counter.textContent);
            let current = 0;
            const increment = target / 50;
            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    current = target;
                    clearInterval(timer);
                }
                counter.textContent = Math.floor(current);
            }, 40);
        });
    }

    filterCandidates(searchTerm) {
        const candidates = document.querySelectorAll('.candidate-card');
        const term = searchTerm.toLowerCase();
        
        candidates.forEach(card => {
            const name = card.querySelector('h5')?.textContent.toLowerCase() || '';
            const skills = card.querySelector('.skills-container')?.textContent.toLowerCase() || '';
            const email = card.querySelector('.text-muted')?.textContent.toLowerCase() || '';
            
            const matches = name.includes(term) || skills.includes(term) || email.includes(term);
            
            if (matches) {
                card.style.display = 'block';
                card.classList.add('fadeInUp');
            } else {
                card.style.display = 'none';
            }
        });
    }

    switchModel(modelType) {
        const currentUrl = new URL(window.location);
        currentUrl.searchParams.set('model', modelType);
        
        // Show loading state
        this.showLoadingOverlay('Switching analysis model...');
        
        // Redirect with new model parameter
        window.location.href = currentUrl.toString();
    }

    showLoadingOverlay(message = 'Loading...') {
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="glass-card p-4 text-center">
                <div class="loading-spinner mx-auto mb-3"></div>
                <h5>${message}</h5>
            </div>
        `;
        
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            backdrop-filter: blur(5px);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
        `;
        
        document.body.appendChild(overlay);
    }

    setupRealTimeUpdates() {
        // Check for real-time updates every 30 seconds
        setInterval(() => {
            this.checkForUpdates();
        }, 30000);
    }

    checkForUpdates() {
        // This would typically make an AJAX call to check for new candidates or updates
        // For now, we'll just update the timestamp
        const timestamp = document.querySelector('.last-updated');
        if (timestamp) {
            timestamp.textContent = `Last updated: ${new Date().toLocaleTimeString()}`;
        }
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-modern alert-${type} alert-dismissible fade show`;
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Add to top of page
        const container = document.querySelector('.container') || document.body;
        container.insertBefore(notification, container.firstChild);
        
        // Auto dismiss after 5 seconds
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(notification);
            bsAlert.close();
        }, 5000);
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.smartScreener = new SmartScreener();
});

// Export for use in other scripts
window.SmartScreener = SmartScreener;
