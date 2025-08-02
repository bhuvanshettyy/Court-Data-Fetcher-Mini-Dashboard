// Main JavaScript for Court Data Fetcher

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Form validation
    initializeFormValidation();
    
    // Search functionality
    initializeSearchFunctionality();
    
    // Download tracking
    initializeDownloadTracking();
    
    // Auto-refresh functionality
    initializeAutoRefresh();
});

function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

function initializeSearchFunctionality() {
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        const searchBtn = searchForm.querySelector('button[type="submit"]');
        const inputs = searchForm.querySelectorAll('input, select');
        
        // Real-time validation
        inputs.forEach(input => {
            input.addEventListener('input', function() {
                validateForm();
            });
            
            input.addEventListener('change', function() {
                validateForm();
            });
        });
        
        function validateForm() {
            const allFilled = Array.from(inputs).every(input => {
                return input.value.trim() !== '';
            });
            
            if (searchBtn) {
                searchBtn.disabled = !allFilled;
            }
        }
        
        // Form submission handling
        searchForm.addEventListener('submit', function(event) {
            if (searchBtn) {
                searchBtn.disabled = true;
                const originalText = searchBtn.innerHTML;
                searchBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Searching...';
                
                // Re-enable after timeout
                setTimeout(() => {
                    searchBtn.disabled = false;
                    searchBtn.innerHTML = originalText;
                }, 30000);
            }
        });
    }
}

function initializeDownloadTracking() {
    const downloadLinks = document.querySelectorAll('a[href*="/download/"]');
    
    downloadLinks.forEach(link => {
        link.addEventListener('click', function(event) {
            const originalText = this.innerHTML;
            this.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Downloading...';
            this.disabled = true;
            
            // Track download
            trackDownload(this.href);
            
            // Reset after delay
            setTimeout(() => {
                this.innerHTML = originalText;
                this.disabled = false;
            }, 5000);
        });
    });
}

function trackDownload(url) {
    // Send analytics event
    if (typeof gtag !== 'undefined') {
        gtag('event', 'download', {
            'event_category': 'court_document',
            'event_label': url
        });
    }
    
    // Log to console for debugging
    console.log('Download initiated:', url);
}

function initializeAutoRefresh() {
    // Auto-refresh search history every 30 seconds
    const historyPage = document.querySelector('.history-page');
    if (historyPage) {
        setInterval(() => {
            refreshHistory();
        }, 30000);
    }
}

function refreshHistory() {
    // This would typically make an AJAX call to refresh the history
    console.log('Auto-refreshing history...');
    
    // Example AJAX call (commented out for now)
    /*
    fetch('/api/history')
        .then(response => response.json())
        .then(data => {
            updateHistoryTable(data);
        })
        .catch(error => {
            console.error('Error refreshing history:', error);
        });
    */
}

function updateHistoryTable(data) {
    // Update the history table with new data
    const tbody = document.querySelector('#historyTable tbody');
    if (tbody && data.searches) {
        // Update table content
        tbody.innerHTML = data.searches.map(search => `
            <tr>
                <td>${search.case_type}</td>
                <td>${search.case_number} / ${search.filing_year}</td>
                <td>${search.timestamp}</td>
                <td>${search.status}</td>
            </tr>
        `).join('');
    }
}

// Utility functions
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Error handling
window.addEventListener('error', function(event) {
    console.error('JavaScript error:', event.error);
    showNotification('An error occurred. Please try again.', 'danger');
});

// Network status monitoring
window.addEventListener('online', function() {
    showNotification('Connection restored.', 'success');
});

window.addEventListener('offline', function() {
    showNotification('You are currently offline.', 'warning');
});

// Export functions for use in templates
window.CourtDataFetcher = {
    showNotification,
    formatFileSize,
    formatDate,
    trackDownload
}; 