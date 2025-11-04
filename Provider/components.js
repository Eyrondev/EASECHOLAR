// Component loader for provider dashboard
document.addEventListener('DOMContentLoaded', function() {
    // Function to load HTML component
    function loadComponent(elementId, filePath) {
        return fetch(filePath)
            .then(response => response.text())
            .then(html => {
                const element = document.getElementById(elementId);
                if (element) {
                    element.innerHTML = html;
                    console.log(`Component ${filePath} loaded successfully`);
                    
                    // Execute any script tags in the loaded HTML
                    const scripts = element.querySelectorAll('script');
                    scripts.forEach(oldScript => {
                        const newScript = document.createElement('script');
                        Array.from(oldScript.attributes).forEach(attr => {
                            newScript.setAttribute(attr.name, attr.value);
                        });
                        newScript.textContent = oldScript.textContent;
                        oldScript.parentNode.replaceChild(newScript, oldScript);
                    });
                    
                    return true;
                }
                return false;
            })
            .catch(error => {
                console.error(`Error loading component ${filePath}:`, error);
                return false;
            });
    }

    // Load components sequentially to ensure proper initialization
    loadComponent('nav-container', 'nav.html')
        .then(() => loadComponent('sidebar-container', 'sidebar.html'))
        .then(() => loadComponent('header-container', 'header.html'))
        .then(() => {
            console.log('All components loaded and scripts executed');
            
            // Wait for scripts to be fully initialized
            setTimeout(() => {
                // Load navigation data
                if (typeof window.loadProviderNav === 'function') {
                    console.log('Calling loadProviderNav...');
                    window.loadProviderNav();
                } else {
                    console.error('loadProviderNav function not found');
                }
                
                // Load sidebar data
                if (typeof window.loadProviderSidebar === 'function') {
                    console.log('Calling loadProviderSidebar...');
                    window.loadProviderSidebar();
                } else {
                    console.error('loadProviderSidebar function not found');
                }
            }, 100);
        });
});

// User menu toggle function (moved from inline)
function toggleUserMenu() {
    const menu = document.getElementById('user-menu');
    if (menu) {
        menu.classList.toggle('hidden');
    }
}

// Close dropdown when clicking outside
document.addEventListener('click', function(event) {
    const userMenu = document.getElementById('user-menu');
    const userButton = event.target.closest('[onclick="toggleUserMenu()"]');
    
    if (userMenu && !userButton && !userMenu.contains(event.target)) {
        userMenu.classList.add('hidden');
    }
});

// Notification functions
function markAsRead(notificationId) {
    console.log(`Marking notification ${notificationId} as read`);
    // In a real application, this would make an API call
}

function markAllAsRead() {
    console.log('Marking all notifications as read');
    // In a real application, this would make an API call
}

// Quick action functions
function createNewScholarship() {
    window.location.href = 'scholarships.html?action=create';
}

function viewPendingApplications() {
    window.location.href = 'applications.html?status=pending';
}

// Search functionality
function performSearch(query) {
    if (query.trim()) {
        console.log(`Searching for: ${query}`);
        // In a real application, this would perform the search
    }
}

// Profile Modal Functions
function openProfileModal() {
    const modal = document.getElementById('profileModal');
    if (modal) {
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden'; // Prevent background scrolling
        
        // Close user menu when opening profile modal
        const userMenu = document.getElementById('user-menu');
        if (userMenu) {
            userMenu.classList.add('hidden');
        }
    }
}

function closeProfileModal() {
    const modal = document.getElementById('profileModal');
    if (modal) {
        modal.classList.add('hidden');
        document.body.style.overflow = 'auto'; // Restore background scrolling
    }
}

function editProfile() {
    closeProfileModal();
    window.location.href = 'settings.html';
}

// Setup modal event listeners after nav component is loaded
function setupModalEventListeners() {
    // Close modal when clicking outside
    const modal = document.getElementById('profileModal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                closeProfileModal();
            }
        });
    }
    
    // Close modal with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const modal = document.getElementById('profileModal');
            if (modal && !modal.classList.contains('hidden')) {
                closeProfileModal();
            }
        }
    });
}