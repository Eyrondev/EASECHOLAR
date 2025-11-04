/**
 * Admin Components Loader
 * Loads sidebar, navigation, and header components for admin pages
 */

document.addEventListener('DOMContentLoaded', function() {
    // Load sidebar component
    loadComponent('sidebar-container', '/Admin/sidebar.html', function() {
        // Sidebar loaded, now set active page
        console.log('Sidebar loaded, setting active page...');
        if (typeof window.setAdminActivePage === 'function') {
            window.setAdminActivePage();
        }
    });
    
    // Load navigation component
    loadComponent('nav-container', '/Admin/nav.html');
    
    // Load header component
    loadComponent('header-container', '/Admin/header.html');
    
    // Check authentication
    checkAdminAuth();
});

/**
 * Load a component into a container
 */
function loadComponent(containerId, componentPath, callback) {
    const container = document.getElementById(containerId);
    if (!container) {
        console.warn(`Container ${containerId} not found`);
        return;
    }

    fetch(componentPath)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Failed to load ${componentPath}`);
            }
            return response.text();
        })
        .then(html => {
            container.innerHTML = html;
            
            // Execute any scripts in the loaded HTML
            const scripts = container.querySelectorAll('script');
            scripts.forEach(script => {
                const newScript = document.createElement('script');
                if (script.src) {
                    newScript.src = script.src;
                } else {
                    newScript.textContent = script.textContent;
                }
                document.body.appendChild(newScript);
            });
            
            // Call callback after a short delay to ensure scripts have executed
            if (callback && typeof callback === 'function') {
                setTimeout(callback, 150);
            }
        })
        .catch(error => {
            console.error(`Error loading component ${componentPath}:`, error);
        });
}

/**
 * Check if user is authenticated as admin
 */
function checkAdminAuth() {
    fetch('/api/auth/status')
        .then(response => response.json())
        .then(data => {
            if (!data.authenticated) {
                window.location.href = '/login.html';
                return;
            }
            
            if (data.user.user_type !== 'ADMIN') {
                alert('Access denied. Admin privileges required.');
                window.location.href = '/index.html';
                return;
            }
        })
        .catch(error => {
            console.error('Error checking authentication:', error);
            window.location.href = '/login.html';
        });
}

/**
 * Format date to readable string
 */
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
    });
}

/**
 * Format datetime to readable string
 */
function formatDateTime(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Get relative time (e.g., "2 hours ago")
 */
function getRelativeTime(dateString) {
    if (!dateString) return 'Never';
    
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    
    return formatDate(dateString);
}

/**
 * Show loading spinner
 */
function showLoading(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = `
            <div class="flex items-center justify-center py-12">
                <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
            </div>
        `;
    }
}

/**
 * Show error message
 */
function showError(containerId, message) {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = `
            <div class="bg-red-50 border border-red-200 rounded-lg p-4">
                <div class="flex items-center">
                    <i class="fas fa-exclamation-circle text-red-500 mr-3"></i>
                    <p class="text-red-800">${message}</p>
                </div>
            </div>
        `;
    }
}

/**
 * Show success message
 */
function showSuccess(message, duration = 3000) {
    const toast = document.createElement('div');
    toast.className = 'fixed top-20 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-slide-in';
    toast.innerHTML = `
        <div class="flex items-center">
            <i class="fas fa-check-circle mr-3"></i>
            <span>${message}</span>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slide-out 0.3s ease-out';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

/**
 * Show warning message
 */
function showWarning(message, duration = 3000) {
    const toast = document.createElement('div');
    toast.className = 'fixed top-20 right-4 bg-yellow-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-slide-in';
    toast.innerHTML = `
        <div class="flex items-center">
            <i class="fas fa-exclamation-triangle mr-3"></i>
            <span>${message}</span>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slide-out 0.3s ease-out';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

/**
 * Confirm dialog
 */
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

/**
 * Format currency
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-PH', {
        style: 'currency',
        currency: 'PHP'
    }).format(amount);
}

/**
 * Get status badge HTML
 */
function getStatusBadge(status) {
    const statusClasses = {
        'VERIFIED': 'bg-green-100 text-green-800',
        'PENDING': 'bg-yellow-100 text-yellow-800',
        'ACTIVE': 'bg-green-100 text-green-800',
        'INACTIVE': 'bg-gray-100 text-gray-800',
        'APPROVED': 'bg-green-100 text-green-800',
        'REJECTED': 'bg-red-100 text-red-800',
        'UNDER_REVIEW': 'bg-blue-100 text-blue-800'
    };
    
    const className = statusClasses[status] || 'bg-gray-100 text-gray-800';
    return `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${className}">${status}</span>`;
}

/**
 * Download file
 */
function downloadFile(filename) {
    window.open(`/uploads/${filename}`, '_blank');
}

// Add custom CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slide-in {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slide-out {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    .animate-slide-in {
        animation: slide-in 0.3s ease-out;
    }
`;
document.head.appendChild(style);
