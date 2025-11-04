// EASECHOLAR Frontend API Integration
// Enhanced with IntellEvalPro patterns

class EasecholarAPI {
    constructor() {
        // Use relative URLs for production deployment (AWS, etc.)
        // This automatically uses the current domain and protocol
        this.baseURL = window.location.origin;
        this.apiURL = `${window.location.origin}/api`;
    }

    // Generic API request method with enhanced error handling
    async request(endpoint, options = {}) {
        const url = `${this.apiURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            credentials: 'same-origin', // Important for session-based auth
            ...options
        };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('API Request Error:', error);
            throw new Error('Network error. Please check your connection.');
        }
    }

    // Authentication status check
    async checkAuthStatus() {
        try {
            const response = await fetch(`${this.apiURL}/auth/status`, {
                credentials: 'same-origin'
            });
            return await response.json();
        } catch (error) {
            console.error('Auth status check failed:', error);
            return { authenticated: false };
        }
    }

    // Enhanced login with session-based authentication
    async login(email, password) {
        try {
            const response = await fetch(`${this.apiURL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin',
                body: JSON.stringify({
                    email: email,
                    password: password
                })
            });

            const data = await response.json();
            
            if (data.success) {
                // Store user data locally for quick access
                localStorage.setItem('user_data', JSON.stringify(data.user));
            }

            return data;
        } catch (error) {
            console.error('Login error:', error);
            return { success: false, message: 'Network error occurred' };
        }
    }

    // Get user profile information
    async getUserProfile() {
        return await this.request('/user/profile');
    }

    // Get dashboard data
    async getDashboardData() {
        return await this.request('/dashboard/data');
    }

    // Student-specific API methods
    async getStudentApplications() {
        return await this.request('/student/applications');
    }

    async getAvailableScholarships() {
        return await this.request('/student/scholarships/available');
    }

    async applyForScholarship(scholarshipId, applicationData) {
        return await this.request('/student/applications', {
            method: 'POST',
            body: JSON.stringify({
                scholarship_id: scholarshipId,
                ...applicationData
            })
        });
    }

    // Provider-specific API methods
    async getProviderScholarships() {
        return await this.request('/provider/scholarships');
    }

    async createScholarship(scholarshipData) {
        return await this.request('/provider/scholarships', {
            method: 'POST',
            body: JSON.stringify(scholarshipData)
        });
    }

    async getApplicationsForScholarship(scholarshipId) {
        return await this.request(`/provider/scholarships/${scholarshipId}/applications`);
    }

    async updateApplicationStatus(applicationId, status, notes = '') {
        return await this.request(`/provider/applications/${applicationId}`, {
            method: 'PATCH',
            body: JSON.stringify({
                status: status,
                reviewer_notes: notes
            })
        });
    }

    // Utility methods
    async logout() {
        try {
            localStorage.removeItem('user_data');
            window.location.href = '/logout';
        } catch (error) {
            console.error('Logout error:', error);
        }
    }

    // Get current user from local storage
    getCurrentUser() {
        const userData = localStorage.getItem('user_data');
        return userData ? JSON.parse(userData) : null;
    }
}

// Create global API instance
const easecholarAPI = new EasecholarAPI();

// Login form handler (enhanced)
async function handleLogin(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    const email = formData.get('email');
    const password = formData.get('password');
    
    // Show loading state
    const submitButton = form.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;
    submitButton.textContent = 'Signing in...';
    submitButton.disabled = true;
    
    try {
        const result = await easecholarAPI.login(email, password);
        
        if (result.success) {
            // Redirect to appropriate dashboard
            window.location.href = result.redirect_url;
        } else {
            // Show error message
            showErrorMessage(result.message || 'Login failed. Please try again.');
        }
    } catch (error) {
        console.error('Login error:', error);
        showErrorMessage('Network error. Please check your connection.');
    } finally {
        // Reset button state
        submitButton.textContent = originalText;
        submitButton.disabled = false;
    }
}

// Utility function to show error messages
function showErrorMessage(message) {
    // Remove existing error messages
    const existingErrors = document.querySelectorAll('.alert-error');
    existingErrors.forEach(error => error.remove());
    
    // Create error element
    const errorDiv = document.createElement('div');
    errorDiv.className = 'bg-red-100 text-red-700 p-4 rounded-md animate-fade-in mb-6 alert-error';
    errorDiv.innerHTML = `
        <div class="flex">
            <div class="flex-shrink-0">
                <i class="fas fa-exclamation-circle mr-2"></i>
            </div>
            <div class="ml-2">
                <p class="text-sm font-medium">${message}</p>
            </div>
        </div>
    `;
    
    // Insert before form
    const form = document.querySelector('form');
    if (form) {
        form.parentNode.insertBefore(errorDiv, form);
    }
}

// Clear field error on input
function clearFieldError(field) {
    field.classList.remove('border-red-500', 'bg-red-50');
    field.classList.add('border-gray-300');
}

// Dashboard initialization
async function initializeDashboard() {
    try {
        const authStatus = await easecholarAPI.checkAuthStatus();
        
        if (!authStatus.authenticated) {
            window.location.href = '/login.html';
            return;
        }
        
        // Load dashboard data
        const dashboardData = await easecholarAPI.getDashboardData();
        
        if (dashboardData.success) {
            updateDashboardUI(dashboardData.data);
        }
    } catch (error) {
        console.error('Dashboard initialization error:', error);
    }
}

// Update dashboard UI with data
function updateDashboardUI(data) {
    // Update user name
    const userNameElements = document.querySelectorAll('[data-user-name]');
    userNameElements.forEach(element => {
        if (data.student_name) {
            element.textContent = data.student_name;
        } else if (data.provider_name) {
            element.textContent = data.provider_name;
        }
    });
    
    // Update statistics
    const statElements = document.querySelectorAll('[data-stat]');
    statElements.forEach(element => {
        const statKey = element.dataset.stat;
        if (data[statKey] !== undefined) {
            element.textContent = data[statKey];
        }
    });
    
    // Update progress bars
    const progressElements = document.querySelectorAll('[data-progress]');
    progressElements.forEach(element => {
        const progressKey = element.dataset.progress;
        if (data[progressKey] !== undefined) {
            element.style.width = `${data[progressKey]}%`;
        }
    });
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on a dashboard page
    if (window.location.pathname.includes('dashboard')) {
        initializeDashboard();
    }
});