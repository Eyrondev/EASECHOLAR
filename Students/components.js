// Component loader for student dashboard
document.addEventListener('DOMContentLoaded', function() {
    // Function to load HTML component
    function loadComponent(elementId, filePath) {
        fetch(filePath)
            .then(response => response.text())
            .then(html => {
                const element = document.getElementById(elementId);
                if (element) {
                    element.innerHTML = html;
                    
                    // Execute scripts in the loaded HTML
                    const scripts = element.querySelectorAll('script');
                    scripts.forEach(oldScript => {
                        const newScript = document.createElement('script');
                        newScript.textContent = oldScript.textContent;
                        oldScript.parentNode.replaceChild(newScript, oldScript);
                    });
                    
                    // Load navigation data after nav component is loaded
                    if (elementId === 'nav-container') {
                        setTimeout(() => {
                            if (typeof window.loadStudentNav === 'function') {
                                window.loadStudentNav();
                            }
                        }, 100);
                    }
                    
                    // Load sidebar data after sidebar component is loaded
                    if (elementId === 'sidebar-container') {
                        setTimeout(() => {
                            if (typeof window.loadStudentSidebar === 'function') {
                                window.loadStudentSidebar();
                            }
                        }, 100);
                    }
                    
                    // Load header data after header component is loaded
                    if (elementId === 'header-container') {
                        setTimeout(() => {
                            if (typeof window.loadStudentHeader === 'function') {
                                window.loadStudentHeader();
                            }
                        }, 100);
                    }
                }
            })
            .catch(error => {
                console.error(`Error loading component ${filePath}:`, error);
            });
    }

    // Load components
    loadComponent('nav-container', 'nav.html');
    loadComponent('sidebar-container', 'sidebar.html');
    loadComponent('header-container', 'header.html');
});

// User menu toggle function (moved from inline)
function toggleUserMenu() {
    const menu = document.getElementById('user-menu');
    if (menu) {
        menu.classList.toggle('hidden');
    }
}