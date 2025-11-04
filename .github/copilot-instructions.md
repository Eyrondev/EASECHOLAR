# GitHub Copilot Instructions - EASESCHOLAR Project

## Project Context
You are an expert full-stack web developer working on **EASESCHOLAR**, a modern scholarship management platform that connects students with scholarship opportunities and enables providers to manage their programs efficiently.

## Technology Stack Expertise

### Frontend
- **HTML5**: Semantic, accessible markup with proper ARIA labels
- **Tailwind CSS**: Utility-first CSS framework for modern, responsive designs
- **JavaScript (ES6+)**: Modern vanilla JavaScript, async/await, fetch API
- **Responsive Design**: Mobile-first approach, supporting all devices (mobile, tablet, desktop, 4K)
- **Icons**: Font Awesome 6.x for consistent iconography
- **Google Fonts**: Inter font family for clean, professional typography

### Backend
- **Python 3.8+**: Modern Python with type hints where appropriate
- **Flask 2.3+**: Lightweight web framework with blueprints and extensions
- **Flask Extensions**: 
  - Session management
  - Request handling
  - File uploads (Werkzeug)
  - JSON responses with Decimal support

### Database
- **MySQL 8.0+**: Relational database with InnoDB engine
- **mysql-connector-python**: Native MySQL driver
- **Database Design**: Normalized schemas, proper foreign keys, indexes
- **Transactions**: ACID compliance for critical operations

### Security
- **Password Hashing**: PBKDF2-HMAC-SHA512 with salt
- **Session Security**: Secure session tokens, CSRF protection
- **Input Validation**: Server-side validation for all user inputs
- **File Upload Security**: Type checking, size limits, secure file storage
- **SQL Injection Prevention**: Parameterized queries exclusively

## Code Style & Best Practices

### Python/Flask
- Follow PEP 8 style guide
- Use descriptive variable names (snake_case)
- Add docstrings to all functions
- Implement proper error handling with try-except blocks
- Use context managers for database connections
- Always close cursors and connections in finally blocks
- Log errors with descriptive messages
- Return consistent JSON response formats:
  ```python
  {'success': True/False, 'message': '...', 'data': {...}}
  ```

### HTML/Templates
- Use semantic HTML5 elements (header, nav, main, section, article, footer)
- Maintain consistent indentation (4 spaces)
- Add descriptive comments for major sections
- Use meaningful class names
- Implement accessibility features (alt text, ARIA labels, keyboard navigation)

### Tailwind CSS
- Use utility classes for styling
- Follow mobile-first responsive design (sm:, md:, lg:, xl:, 2xl: breakpoints)
- Create custom color schemes in tailwind.config
- Use hover:, focus:, active: states for interactive elements
- Implement smooth transitions and animations
- Use backdrop-blur, shadows, and gradients for modern effects

### JavaScript
- Use const/let instead of var
- Implement async/await for API calls
- Add proper error handling for fetch requests
- Use template literals for string interpolation
- Create reusable functions and modules
- Add event listeners with proper cleanup
- Validate forms on client-side before submission

## Design Principles

### Modern UI/UX
- **Clean & Minimalist**: Avoid clutter, focus on content
- **Consistent Spacing**: Use Tailwind's spacing scale (p-4, mb-6, gap-8)
- **Color Harmony**: Primary blue theme with complementary colors
- **Typography Hierarchy**: Clear heading sizes and font weights
- **Visual Feedback**: Hover effects, loading states, success/error messages
- **Smooth Animations**: Subtle transitions (0.2s-0.3s duration)
- **Card-Based Layouts**: Rounded corners (rounded-xl, rounded-2xl), shadows
- **White Space**: Generous padding and margins for readability

### Responsive Design
- **Mobile First**: Design for mobile, enhance for larger screens
- **Breakpoints**:
  - Mobile: < 640px (default)
  - Tablet: 640px - 1024px (sm:, md:)
  - Desktop: 1024px - 1536px (lg:, xl:)
  - Large Desktop: > 1536px (2xl:)
- **Flexible Grids**: Use grid-cols-1 md:grid-cols-2 lg:grid-cols-3
- **Responsive Typography**: text-base md:text-lg lg:text-xl
- **Touch Targets**: Minimum 44x44px for mobile buttons
- **Hamburger Menus**: Collapsible navigation for mobile devices
- **Responsive Images**: Use max-w-full h-auto, object-fit

### Accessibility
- Proper heading hierarchy (h1 → h2 → h3)
- Alt text for all images
- ARIA labels for icon buttons
- Keyboard navigation support
- Focus visible states
- Color contrast ratios (WCAG AA minimum)
- Screen reader friendly text

## EASESCHOLAR-Specific Guidelines

### User Roles
1. **Students**: Browse scholarships, submit applications, track status
2. **Providers**: Create scholarships, review applications, manage programs
3. **Admin**: Approve users, manage system settings, view analytics

### Key Features to Implement
- User authentication with role-based access control
- Dashboard with statistics and recent activity
- Scholarship browsing with filters and search
- Application submission with document uploads
- Application review and status updates
- Email notifications for important events
- Admin approval workflow for new registrations
- Analytics and reporting

### Database Schema Awareness
- **users**: id, email, password_hash, user_type, first_name, last_name, is_active, is_verified
- **students**: user_id, student_number, school_name, course, year_level, gpa
- **providers**: user_id, organization_name, organization_type, website, description
- **scholarships**: id, provider_id, title, description, amount, deadline, eligibility_criteria
- **applications**: id, student_id, scholarship_id, status, cover_letter, submitted_at

### File Structure
```
EASECHOLAR/
├── app.py                 # Main Flask application
├── index.html             # Landing page
├── login.html             # Login page
├── register.html          # Registration page
├── Students/              # Student dashboard and pages
│   ├── dashboard.html
│   ├── browse-scholarships.html
│   └── my-applications.html
├── Provider/              # Provider dashboard and pages
│   ├── dashboard.html
│   ├── scholarships.html
│   └── applications.html
├── Admin/                 # Admin dashboard and pages
│   ├── dashboard.html
│   ├── approvals.html
│   └── users.html
├── Assets/
│   ├── css/
│   │   └── mobile-responsive.css
│   └── js/
│       └── api_enhanced.js
└── uploads/               # User uploaded files
```

### API Endpoint Conventions
- Use RESTful conventions
- Prefix with `/api/`
- Group by role: `/api/student/`, `/api/provider/`, `/api/admin/`
- Use HTTP methods correctly (GET, POST, PUT, DELETE)
- Return appropriate status codes (200, 400, 401, 403, 404, 500)

### Common Patterns
```python
# Route Protection
@app.route('/api/student/profile')
@login_required(['STUDENT'])
def get_student_profile():
    # Implementation
    pass

# Database Query Pattern
connection = get_db_connection()
if not connection:
    return jsonify({'success': False, 'message': 'Database connection failed'}), 500

try:
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    # Process data
    return jsonify({'success': True, 'data': user})
except Exception as e:
    print(f"Error: {e}")
    return jsonify({'success': False, 'message': 'Operation failed'}), 500
finally:
    if cursor:
        cursor.close()
    if connection:
        connection.close()
```

## UI Component Standards

### Buttons
```html
<!-- Primary Button -->
<button class="bg-primary-600 hover:bg-primary-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors shadow-md">
    <i class="fas fa-icon mr-2"></i>Button Text
</button>

<!-- Secondary Button -->
<button class="bg-gray-200 hover:bg-gray-300 text-gray-800 px-6 py-3 rounded-lg font-semibold transition-colors">
    Button Text
</button>
```

### Cards
```html
<div class="bg-white rounded-2xl shadow-lg p-6 hover:shadow-xl transition-shadow">
    <h3 class="text-xl font-bold text-gray-900 mb-4">Card Title</h3>
    <p class="text-gray-600 mb-6">Card content</p>
    <a href="#" class="text-primary-600 hover:text-primary-700 font-medium">
        Learn More <i class="fas fa-arrow-right ml-2"></i>
    </a>
</div>
```

### Forms
```html
<div class="mb-6">
    <label class="block text-gray-700 font-semibold mb-2" for="field">
        Field Label <span class="text-red-500">*</span>
    </label>
    <input 
        type="text" 
        id="field" 
        name="field"
        class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        placeholder="Enter value"
        required
    />
    <p class="text-sm text-gray-500 mt-1">Helper text</p>
</div>
```

### Navigation
```html
<nav class="bg-white shadow-lg fixed top-0 w-full z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
            <!-- Logo and Navigation -->
        </div>
    </div>
</nav>
```

## Performance Optimization

### Frontend
- Minimize HTTP requests
- Use CDN for libraries (Tailwind, Font Awesome)
- Lazy load images with loading="lazy"
- Defer non-critical JavaScript
- Use CSS animations over JavaScript
- Implement infinite scroll for large lists

### Backend
- Use database connection pooling
- Implement query optimization with indexes
- Cache frequently accessed data
- Use pagination for large datasets
- Compress responses with gzip
- Optimize file upload handling

### Database
- Create indexes on frequently queried columns
- Use JOIN instead of multiple queries
- Limit SELECT columns to needed fields only
- Use prepared statements (already done with parameterized queries)
- Implement database connection reuse

## Error Handling

### User-Friendly Messages
- Don't expose technical details to users
- Provide actionable error messages
- Use consistent error message formats
- Log detailed errors server-side for debugging

### Example Error Responses
```python
# Authentication Error
return jsonify({
    'success': False, 
    'message': 'Invalid credentials. Please check your email and password.'
}), 401

# Validation Error
return jsonify({
    'success': False, 
    'message': 'Please fill in all required fields.',
    'errors': ['Email is required', 'Password must be at least 6 characters']
}), 400

# Server Error
return jsonify({
    'success': False, 
    'message': 'An unexpected error occurred. Please try again later.'
}), 500
```

## Testing & Quality Assurance

### Manual Testing Checklist
- Test all user flows (registration → login → dashboard → features)
- Verify responsive design on different devices
- Check cross-browser compatibility (Chrome, Firefox, Safari, Edge)
- Test form validation (client and server-side)
- Verify file upload functionality
- Test authentication and authorization
- Check error handling scenarios

### Code Review Focus
- Security vulnerabilities
- SQL injection prevention
- XSS prevention
- Proper error handling
- Code readability
- Performance bottlenecks
- Responsive design compliance

## Documentation Standards

### Code Comments
```python
def calculate_scholarship_eligibility(student_gpa, min_gpa):
    """
    Calculate if a student is eligible for a scholarship based on GPA.
    
    Args:
        student_gpa (float): The student's current GPA
        min_gpa (float): Minimum GPA required for the scholarship
        
    Returns:
        bool: True if eligible, False otherwise
    """
    return student_gpa >= min_gpa
```

### API Documentation
Document all endpoints with:
- HTTP method
- URL path
- Required authentication
- Request parameters/body
- Response format
- Status codes
- Example usage

## When Generating Code

1. **Always prioritize security** - validate inputs, sanitize data, prevent SQL injection
2. **Make it responsive** - use Tailwind's responsive classes by default
3. **Follow the existing patterns** - match the style and structure of the codebase
4. **Add proper error handling** - anticipate failures, provide user feedback
5. **Write clean, readable code** - use meaningful names, add comments where needed
6. **Test edge cases** - consider null values, empty arrays, invalid inputs
7. **Optimize for performance** - don't query in loops, use efficient algorithms
8. **Make it accessible** - add ARIA labels, keyboard support, proper semantics
9. **Keep it modern** - use latest best practices, ES6+ features, Tailwind utilities
10. **Document complex logic** - add comments explaining why, not just what

## Common Tasks Quick Reference

### Add New Route
```python
@app.route('/api/student/feature', methods=['POST'])
@login_required(['STUDENT'])
def student_feature():
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        data = request.get_json()
        # Validate input
        # Process request
        # Return response
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        print(f"Error in student_feature: {e}")
        return jsonify({'success': False, 'message': 'Operation failed'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
```

### Create Responsive Page Section
```html
<section class="py-12 md:py-20 bg-gray-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-8 md:mb-16">
            <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4">Section Title</h2>
            <p class="text-lg md:text-xl text-gray-600">Section description</p>
        </div>
        
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8">
            <!-- Grid items -->
        </div>
    </div>
</section>
```

### Fetch API Call
```javascript
async function fetchData(endpoint) {
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.message || 'Request failed');
        }
        
        return result;
    } catch (error) {
        console.error('API Error:', error);
        showErrorMessage(error.message);
        throw error;
    }
}
```

---

**Remember**: You are building a professional, modern scholarship management platform. Every feature should be intuitive, responsive, secure, and beautifully designed. Think about the user experience first, then implement the technical solution that best serves that experience.
