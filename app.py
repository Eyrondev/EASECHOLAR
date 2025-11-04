#!/usr/bin/env python3
"""
EASESCHOLAR Flask Backend Application
Handles authentication and backend functionality for the EASESCHOLAR scholarship platform
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify as flask_jsonify, make_response, send_from_directory
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
import mysql.connector
from mysql.connector import Error
import hashlib
import secrets
import binascii
import os
from datetime import datetime, timedelta
from decimal import Decimal
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Custom JSON encoder to handle Decimal types
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

# Custom jsonify function that handles Decimal types
def jsonify(*args, **kwargs):
    """Custom jsonify that handles Decimal types."""
    if args and kwargs:
        raise TypeError('jsonify() behavior undefined when passed both args and kwargs')
    elif len(args) == 1:
        data = args[0]
    else:
        data = dict(*args, **kwargs) if args else kwargs
    
    # Convert data using our custom encoder
    json_str = json.dumps(data, cls=DecimalEncoder)
    response = make_response(json_str)
    response.mimetype = 'application/json'
    return response

app = Flask(__name__, template_folder='.', static_folder='.', static_url_path='')
app.secret_key = os.environ.get('SECRET_KEY', 'easescholar_secret_key_2025')

# File upload configuration
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Email configuration for password reset
# All credentials are loaded from .env file for security
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER') or os.environ.get('MAIL_USERNAME')

# Validate email configuration
if not app.config['MAIL_USERNAME'] or not app.config['MAIL_PASSWORD']:
    print("⚠️  WARNING: Email credentials not found in environment variables!")
    print("   Email functionality (password reset) will NOT work.")
    print("   Please set MAIL_USERNAME and MAIL_PASSWORD in your .env file")
else:
    print(f"✓ Email configured: {app.config['MAIL_USERNAME']}")

# Initialize Flask-Mail
mail = Mail(app)

# Configure Flask to use custom JSON encoder for Decimal types
try:
    # For Flask 2.3.x and earlier
    app.json_encoder = DecimalEncoder
except AttributeError:
    # For newer Flask versions
    from flask.json.provider import JSONProvider
    
    class DecimalJSONProvider(JSONProvider):
        def dumps(self, obj, **kwargs):
            return json.dumps(obj, cls=DecimalEncoder, **kwargs)
        
        def loads(self, s):
            return json.loads(s)
    
    app.json = DecimalJSONProvider(app)

# Database configuration
# Load from environment variables for security
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'database-1.cx4waogceerc.ap-southeast-2.rds.amazonaws.com'),
    'user': os.environ.get('DB_USER', 'admin'),
    'password': os.environ.get('DB_PASSWORD', '12345678'),
    'database': os.environ.get('DB_NAME', 'easecholar_db'),
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}

# Validate database configuration
print(f"✓ Database configured: {DB_CONFIG['user']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}")

def get_db_connection():
    """Create and return a database connection with enhanced error handling"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL database: {err}")
        return None
    except Exception as e:
        print(f"Unexpected error connecting to database: {e}")
        return None

# Enhanced password hashing functions (based on IntellEvalPro pattern)
def generate_password_hash(password):
    """Hash a password for storing."""
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), 
                                salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')

def check_password_hash(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    try:
        if len(stored_password) >= 64:
            salt = stored_password[:64]
            stored_hash = stored_password[64:]
            pwdhash = hashlib.pbkdf2_hmac('sha512', 
                                        provided_password.encode('utf-8'), 
                                        salt.encode('ascii'), 
                                        100000)
            pwdhash = binascii.hexlify(pwdhash).decode('ascii')
            return pwdhash == stored_hash
    except Exception as e:
        print(f"Error checking password: {e}")
        
    return False

# File upload utility functions
def allowed_file(filename):
    """Check if file has allowed extension"""
    ALLOWED_EXTENSIONS = {'pdf'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_file_upload(file, file_type='document'):
    """Validate uploaded file"""
    errors = []
    
    if not file:
        errors.append(f'{file_type} is required.')
        return errors
    
    if file.filename == '':
        errors.append(f'{file_type} filename cannot be empty.')
        return errors
    
    if not allowed_file(file.filename):
        errors.append(f'{file_type} must be a PDF file.')
    
    # Check file size (5MB limit)
    file.seek(0, os.SEEK_END)
    file_length = file.tell()
    file.seek(0)  # Reset to beginning
    
    if file_length > 5 * 1024 * 1024:  # 5MB
        errors.append(f'{file_type} file size must be less than 5MB.')
    
    return errors

def save_uploaded_file(file, user_id, file_prefix):
    """Save uploaded file with secure filename"""
    if file and allowed_file(file.filename):
        # Create uploads directory if it doesn't exist
        upload_dir = app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        # Generate secure filename
        filename = f"{file_prefix}_{user_id}_{secrets.token_hex(8)}.pdf"
        filepath = os.path.join(upload_dir, filename)
        
        file.save(filepath)
        return filename
    
    return None

from functools import wraps

# Decorator for route protection
def login_required(user_types=None):
    """Decorator to require login and optionally specific user types"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'error')
                return redirect(url_for('login'))
            
            if user_types and session.get('user_type') not in user_types:
                flash('You do not have permission to access this page.', 'error')
                return redirect(url_for('index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Helper Functions

def get_user_dashboard_data(user_id, user_type):
    """Get dashboard data specific to user type"""
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        if user_type == 'STUDENT':
            # Get student-specific dashboard data
            query = """
                SELECT 
                    (SELECT COUNT(*) FROM applications a 
                     JOIN students s ON a.student_id = s.id 
                     WHERE s.user_id = %s) as total_applications,
                    (SELECT COUNT(*) FROM applications a 
                     JOIN students s ON a.student_id = s.id 
                     WHERE s.user_id = %s AND a.status = 'PENDING') as pending_applications,
                    (SELECT COUNT(*) FROM applications a 
                     JOIN students s ON a.student_id = s.id 
                     WHERE s.user_id = %s AND a.status = 'APPROVED') as approved_applications,
                    (SELECT COUNT(*) FROM scholarships 
                     WHERE status = 'ACTIVE' AND application_deadline >= NOW()) as available_scholarships
            """
            cursor.execute(query, (user_id, user_id, user_id))
            
        elif user_type == 'PROVIDER':
            # Get provider-specific dashboard data
            query = """
                SELECT 
                    (SELECT COUNT(*) FROM scholarships sch 
                     JOIN providers p ON sch.provider_id = p.id 
                     WHERE p.user_id = %s) as total_scholarships,
                    (SELECT COUNT(*) FROM scholarships sch 
                     JOIN providers p ON sch.provider_id = p.id 
                     WHERE p.user_id = %s AND sch.status = 'ACTIVE') as active_scholarships,
                    (SELECT COUNT(*) FROM applications a 
                     JOIN scholarships sch ON a.scholarship_id = sch.id 
                     JOIN providers p ON sch.provider_id = p.id 
                     WHERE p.user_id = %s) as total_applicants,
                    (SELECT COUNT(*) FROM applications a 
                     JOIN scholarships sch ON a.scholarship_id = sch.id 
                     JOIN providers p ON sch.provider_id = p.id 
                     WHERE p.user_id = %s AND a.status = 'PENDING') as pending_applications
            """
            cursor.execute(query, (user_id, user_id, user_id, user_id))
        
        result = cursor.fetchone()
        return result if result else {}
        
    except Exception as e:
        print(f"Error fetching dashboard data: {e}")
        return {}
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_admin_dashboard_data():
    """Get admin dashboard data with system statistics"""
    connection = get_db_connection()
    if not connection:
        return {}
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Get comprehensive admin statistics
        query = """
            SELECT 
                (SELECT COUNT(*) FROM users) as total_users,
                (SELECT COUNT(*) FROM users WHERE user_type = 'STUDENT') as total_students,
                (SELECT COUNT(*) FROM users WHERE user_type = 'PROVIDER') as total_providers,
                (SELECT COUNT(*) FROM users WHERE user_type = 'ADMIN') as total_admins,
                (SELECT COUNT(*) FROM users WHERE is_active = 1) as active_users,
                (SELECT COUNT(*) FROM users WHERE is_verified = 0 AND user_type IN ('STUDENT', 'PROVIDER')) as pending_approvals,
                (SELECT COUNT(*) FROM users WHERE is_verified = 1 AND user_type = 'STUDENT') as verified_students,
                (SELECT COUNT(*) FROM users WHERE is_verified = 1 AND user_type = 'PROVIDER') as verified_providers,
                (SELECT COUNT(*) FROM scholarships) as total_scholarships,
                (SELECT COUNT(*) FROM scholarships WHERE is_active = 1) as active_scholarships,
                (SELECT COUNT(*) FROM applications) as total_applications,
                (SELECT COUNT(*) FROM applications WHERE status = 'PENDING') as pending_applications,
                (SELECT COUNT(*) FROM applications WHERE status = 'APPROVED') as approved_applications,
                (SELECT COUNT(*) FROM applications WHERE status = 'REJECTED') as rejected_applications,
                (SELECT COUNT(*) FROM applications WHERE status = 'UNDER_REVIEW') as review_applications,
                (SELECT COUNT(*) FROM users WHERE DATE(created_at) = CURDATE()) as new_users_today,
                (SELECT COUNT(*) FROM users WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)) as new_users_week,
                (SELECT COUNT(*) FROM users WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)) as new_users_this_month,
                (SELECT COUNT(*) FROM scholarships WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)) as new_scholarships_this_month,
                (SELECT COUNT(*) FROM applications WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)) as new_applications_this_month,
                (SELECT COUNT(*) FROM users WHERE created_at >= DATE_SUB(NOW(), INTERVAL 60 DAY) AND created_at < DATE_SUB(NOW(), INTERVAL 30 DAY)) as users_last_month,
                (SELECT COUNT(*) FROM scholarships WHERE created_at >= DATE_SUB(NOW(), INTERVAL 60 DAY) AND created_at < DATE_SUB(NOW(), INTERVAL 30 DAY)) as scholarships_last_month,
                (SELECT COUNT(*) FROM applications WHERE created_at >= DATE_SUB(NOW(), INTERVAL 60 DAY) AND created_at < DATE_SUB(NOW(), INTERVAL 30 DAY)) as applications_last_month
        """
        cursor.execute(query)
        result = cursor.fetchone()
        
        if result:
            # Calculate growth percentages based on actual data with better edge case handling
            users_this_month = result.get('new_users_this_month', 0) or 0
            users_last_month = result.get('users_last_month', 0) or 0
            
            if users_last_month > 0:
                result['users_growth'] = ((users_this_month - users_last_month) / users_last_month * 100)
            elif users_this_month > 0:
                result['users_growth'] = 100.0  # Show 100% growth if we have new data but no previous data
            else:
                result['users_growth'] = 0.0
            
            scholarships_this_month = result.get('new_scholarships_this_month', 0) or 0
            scholarships_last_month = result.get('scholarships_last_month', 0) or 0
            
            if scholarships_last_month > 0:
                result['scholarships_growth'] = ((scholarships_this_month - scholarships_last_month) / scholarships_last_month * 100)
            elif scholarships_this_month > 0:
                result['scholarships_growth'] = 100.0
            else:
                result['scholarships_growth'] = 0.0
            
            apps_this_month = result.get('new_applications_this_month', 0) or 0
            apps_last_month = result.get('applications_last_month', 0) or 0
            
            if apps_last_month > 0:
                result['applications_growth'] = ((apps_this_month - apps_last_month) / apps_last_month * 100)
            elif apps_this_month > 0:
                result['applications_growth'] = 100.0
            else:
                result['applications_growth'] = 0.0
            
            # If any of the application status counts are None, set to 0
            result['approved_applications'] = result.get('approved_applications', 0) or 0
            result['rejected_applications'] = result.get('rejected_applications', 0) or 0
            result['review_applications'] = result.get('review_applications', 0) or 0
            result['pending_applications'] = result.get('pending_applications', 0) or 0
            
            # Ensure monthly counts are not None
            result['new_users_this_month'] = result.get('new_users_this_month', 0) or 0
            result['new_scholarships_this_month'] = result.get('new_scholarships_this_month', 0) or 0
            result['new_applications_this_month'] = result.get('new_applications_this_month', 0) or 0
            
            print(f"📊 Dashboard Stats: Users={result['total_users']}, Apps={result['total_applications']}, Monthly Growth: Users={result['users_growth']:.1f}%, Apps={result['applications_growth']:.1f}%")
            
        return result if result else {}
        
    except Exception as e:
        print(f"Error fetching admin dashboard data: {e}")
        import traceback
        traceback.print_exc()
        return {}
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def initialize_admin_user():
    """Initialize admin user if not exists"""
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Check if admin user exists
            cursor.execute("SELECT * FROM users WHERE email = 'admin@gmail.com'")
            admin = cursor.fetchone()
            
            if not admin:
                # Create admin user
                hashed_password = generate_password_hash('12345')
                now = datetime.now()
                
                insert_query = """
                INSERT INTO users (email, password_hash, user_type, first_name, last_name, 
                                 is_active, is_verified, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                values = (
                    'admin@gmail.com',
                    hashed_password,
                    'ADMIN',
                    'System',
                    'Administrator',
                    1,
                    1,
                    now,
                    now
                )
                
                cursor.execute(insert_query, values)
                connection.commit()
                print("Admin user created successfully")
            else:
                # Admin user exists, check if user_type is set correctly
                if not admin.get('user_type') or admin['user_type'] == '':
                    print(f"Fixing admin user_type (currently: '{admin.get('user_type', 'NULL')}')")
                    update_query = "UPDATE users SET user_type = 'ADMIN' WHERE email = 'admin@gmail.com'"
                    cursor.execute(update_query)
                    connection.commit()
                    print("Admin user_type updated to ADMIN")
            
        except Exception as e:
            print(f"Error initializing admin user: {e}")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

# Maintenance Mode Middleware
@app.before_request
def check_maintenance_mode():
    """Check if maintenance mode is enabled and block public access"""
    # Get the current path
    path = request.path
    
    # Skip maintenance check for:
    # 1. Admin routes (admins can always access)
    # 2. Static files
    # 3. API endpoints (will be checked individually if needed)
    # 4. Login/logout routes (need to allow login)
    # 5. Maintenance page itself
    
    excluded_paths = [
        '/Admin/',
        '/static/',
        '/uploads/',
        '/login',
        '/logout',
        '/api/auth/login',
        '/api/auth/logout',
        '/api/auth/status',
        '/maintenance.html',
        '/api/admin/system-settings'  # Allow checking/changing settings
    ]
    
    # Check if current path should be excluded
    for excluded in excluded_paths:
        if path.startswith(excluded):
            return None
    
    # If user is admin, allow access
    if session.get('user_type') == 'ADMIN':
        return None
    
    # Check maintenance mode status
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT setting_value FROM system_settings 
                WHERE setting_key = 'maintenance_mode'
            """)
            result = cursor.fetchone()
            
            # If maintenance mode is enabled, show maintenance page
            if result and (result['setting_value'] == '1' or result['setting_value'] == 'true'):
                # Return maintenance page with 503 status
                return render_template('maintenance.html'), 503
                
        except Exception as e:
            # If there's an error checking maintenance mode, allow access
            print(f"Error checking maintenance mode: {e}")
            pass
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    return None

# Routes

# Route to serve uploaded files
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    try:
        print(f"=== FILE SERVING DEBUG ===")
        print(f"1. Original filename from URL: {filename}")
        
        # Normalize path separators for Windows compatibility
        filename = filename.replace('\\', '/')
        print(f"2. After replacing backslashes: {filename}")
        
        # Remove 'uploads/' prefix if present (route already has it)
        if filename.startswith('uploads/'):
            filename = filename[8:]  # Remove 'uploads/' prefix
            print(f"3. After removing 'uploads/' prefix: {filename}")
        
        upload_dir = os.path.abspath(app.config['UPLOAD_FOLDER'])
        print(f"4. Upload directory: {upload_dir}")
        
        # Convert forward slashes to OS-specific separators
        file_path = filename.replace('/', os.sep)
        print(f"5. File path with OS separators: {file_path}")
        
        # Check if file exists
        full_path = os.path.join(upload_dir, file_path)
        print(f"6. Full path to check: {full_path}")
        print(f"7. File exists: {os.path.exists(full_path)}")
        
        if not os.path.exists(full_path):
            print(f"ERROR: File not found at: {full_path}")
            # List directory contents for debugging
            dir_path = os.path.dirname(full_path)
            if os.path.exists(dir_path):
                print(f"Directory exists. Contents: {os.listdir(dir_path)}")
            else:
                print(f"Directory doesn't exist: {dir_path}")
            return "File not found", 404
        
        print(f"8. Serving file successfully")
        # Use send_file instead of send_from_directory for better control
        from flask import send_file
        return send_file(full_path)
    except Exception as e:
        print(f"=== ERROR SERVING FILE ===")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return f"Error: {str(e)}", 500

@app.route('/')
def index():
    """Enhanced Home page - handle authenticated users"""
    if 'user_id' in session:
        # User is logged in, show personalized landing or redirect to dashboard
        user_type = session.get('user_type')
        user_name = session.get('first_name', 'User')
        
        # You can either:
        # 1. Redirect to dashboard directly
        # return redirect(url_for('student_dashboard' if user_type == 'STUDENT' else 'provider_dashboard'))
        
        # 2. Or show personalized landing page (current approach)
        return render_template('index.html', 
                             authenticated=True, 
                             user_name=user_name, 
                             user_type=user_type)
    
    # User not logged in - show regular landing page
    return render_template('index.html', authenticated=False)

@app.route('/login', methods=['GET', 'POST'])
@app.route('/login.html', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        if not email or not password:
            return render_template('login.html', error='Please fill in all required fields.')
        
        connection = get_db_connection()
        if not connection:
            return render_template('login.html', error='Database connection failed. Please try again later.')
        
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Query user by email only
            query = """
                SELECT id, email, password_hash, user_type, first_name, last_name, 
                       is_active, is_verified, last_login 
                FROM users 
                WHERE email = %s
            """
            cursor.execute(query, (email,))
            user = cursor.fetchone()
            
            if user and check_password_hash(user['password_hash'], password):
                # Check if user is active
                if not user['is_active']:
                    return render_template('login.html', error='Your account has been deactivated. Please contact support.')
                
                # Check if user is verified (approved by admin)
                # Admin accounts are automatically verified, so they can always login
                if not user['is_verified'] and user['user_type'] != 'ADMIN':
                    user_type_display = 'student' if user['user_type'] == 'STUDENT' else 'provider'
                    return render_template('login.html', 
                                         error=f'Your {user_type_display} registration is pending approval. '
                                               f'Please wait 2-3 business days for the administrator to review your application. '
                                               f'You will be able to login once your account has been approved. '
                                               f'Thank you for your patience!')
                
                # Update last login
                update_query = "UPDATE users SET last_login = %s WHERE id = %s"
                cursor.execute(update_query, (datetime.now(), user['id']))
                connection.commit()
                
                # Store comprehensive user information in session
                session.permanent = True  # Make session permanent
                session['user_id'] = user['id']
                session['email'] = user['email']
                session['user_type'] = user['user_type']
                session['first_name'] = user['first_name']
                session['last_name'] = user['last_name']
                session['full_name'] = f"{user['first_name']} {user['last_name']}"
                session['is_verified'] = user['is_verified']
                session['login_time'] = datetime.now().isoformat()
                
                # Flash success message
                flash(f'Welcome back, {user["first_name"]}!', 'success')
                
                # Enhanced role-based redirection
                if user['user_type'] == 'STUDENT':
                    return redirect(url_for('student_dashboard'))
                elif user['user_type'] == 'PROVIDER':
                    return redirect(url_for('provider_dashboard'))
                elif user['user_type'] == 'ADMIN':
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('index'))
                    
            else:
                return render_template('login.html', error='Invalid credentials.')
                
        except Error as e:
            print(f"Database error during login: {e}")
            return render_template('login.html', error='An error occurred during login. Please try again.')
            
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    # GET request - show login form
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Handle user logout"""
    session.clear()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
@app.route('/register.html', methods=['GET', 'POST'])
def register():
    """Handle user registration with wizard form"""
    if request.method == 'POST':
        # Get basic form data
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        user_type = request.form.get('user_type', 'STUDENT').upper()
        phone_number = request.form.get('phone_number', '').strip()
        
        # Get student-specific fields
        student_number = request.form.get('student_number', '').strip()
        school_name = request.form.get('school_name', '').strip()
        course = request.form.get('course', '').strip()
        year_level = request.form.get('year_level', '').strip()
        gpa = request.form.get('gpa', '').strip()
        expected_graduation = request.form.get('expected_graduation', '').strip()
        
        # Get provider-specific fields
        organization_name = request.form.get('organization_name', '').strip()
        organization_type = request.form.get('organization_type', '').strip()
        website = request.form.get('website', '').strip()
        description = request.form.get('description', '').strip()
        
        # Validation
        errors = []
        
        if not all([email, password, confirm_password, first_name, last_name]):
            errors.append('All required fields must be filled.')
        
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        if len(password) < 6:
            errors.append('Password must be at least 6 characters long.')
        
        if '@' not in email or '.' not in email:
            errors.append('Please enter a valid email address.')
        
        if user_type not in ['STUDENT', 'PROVIDER']:
            errors.append('Invalid user type selected.')
        
        # User type specific validation
        if user_type == 'STUDENT':
            if not student_number:
                errors.append('Student number is required.')
            if not school_name:
                errors.append('School name is required.')
        elif user_type == 'PROVIDER':
            if not organization_name:
                errors.append('Organization name is required.')
        
        # File validation for students
        if user_type == 'STUDENT':
            cor_file = request.files.get('cor_file')
            coe_file = request.files.get('coe_file')
            
            if not cor_file or cor_file.filename == '':
                errors.append('Certificate of Registration (COR) is required.')
            elif not cor_file.filename.lower().endswith('.pdf'):
                errors.append('COR file must be a PDF.')
            
            if not coe_file or coe_file.filename == '':
                errors.append('Certificate of Enrollment (COE) is required.')
            elif not coe_file.filename.lower().endswith('.pdf'):
                errors.append('COE file must be a PDF.')
        
        # File validation for providers
        if user_type == 'PROVIDER':
            business_reg_file = request.files.get('business_registration')
            if not business_reg_file or business_reg_file.filename == '':
                errors.append('Business registration document is required.')
            elif not business_reg_file.filename.lower().endswith('.pdf'):
                errors.append('Business registration file must be a PDF.')
        
        if errors:
            return jsonify({'error': ' '.join(errors)}), 400
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed. Please try again later.'}), 500
        
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Check if email already exists
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                return jsonify({'error': 'An account with this email already exists.'}), 400
            
            # Hash password using enhanced method
            password_hash = generate_password_hash(password)
            
            # Generate verification token
            verification_token = secrets.token_urlsafe(32)
            
            # Insert new user
            insert_query = """
                INSERT INTO users (email, password_hash, user_type, first_name, last_name, 
                                 phone_number, is_active, is_verified, verification_token, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            now = datetime.now()
            values = (email, password_hash, user_type, first_name, last_name, 
                     phone_number, True, False, verification_token, now, now)
            
            cursor.execute(insert_query, values)
            user_id = cursor.lastrowid
            
            # Handle file uploads
            upload_dir = 'uploads'
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            # Create additional profile table entry based on user type
            if user_type == 'STUDENT':
                # Save uploaded documents
                cor_filename = None
                coe_filename = None
                transcript_filename = None
                
                if cor_file:
                    cor_filename = f"cor_{user_id}_{secrets.token_hex(8)}.pdf"
                    cor_file.save(os.path.join(upload_dir, cor_filename))
                
                if coe_file:
                    coe_filename = f"coe_{user_id}_{secrets.token_hex(8)}.pdf"
                    coe_file.save(os.path.join(upload_dir, coe_filename))
                
                transcript_file = request.files.get('transcript_file')
                if transcript_file and transcript_file.filename:
                    transcript_filename = f"transcript_{user_id}_{secrets.token_hex(8)}.pdf"
                    transcript_file.save(os.path.join(upload_dir, transcript_filename))
                
                student_query = """
                    INSERT INTO students (user_id, student_number, school_name, course, year_level, 
                                        gpa, expected_graduation_date, cor_document, coe_document, 
                                        transcript_document, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                # Handle date conversion
                expected_grad_date = None
                if expected_graduation:
                    try:
                        expected_grad_date = datetime.strptime(expected_graduation, '%Y-%m-%d').date()
                    except ValueError:
                        pass
                
                # Handle GPA conversion
                gpa_value = None
                if gpa:
                    try:
                        gpa_value = float(gpa)
                    except ValueError:
                        pass
                
                cursor.execute(student_query, (
                    user_id, student_number, school_name, course, year_level,
                    gpa_value, expected_grad_date, cor_filename, coe_filename,
                    transcript_filename, now, now
                ))
                
            elif user_type == 'PROVIDER':
                # Save business registration document
                business_reg_filename = None
                business_reg_file = request.files.get('business_registration')
                
                if business_reg_file:
                    business_reg_filename = f"business_reg_{user_id}_{secrets.token_hex(8)}.pdf"
                    business_reg_file.save(os.path.join(upload_dir, business_reg_filename))
                
                provider_query = """
                    INSERT INTO providers (user_id, organization_name, organization_type, website,
                                         description, business_registration_document, is_verified, 
                                         created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(provider_query, (
                    user_id, organization_name, organization_type, website,
                    description, business_reg_filename, False, now, now
                ))
            
            connection.commit()
            
            return jsonify({
                'success': True,
                'message': 'Registration successful! Please check your email to verify your account.'
            })
            
        except Error as e:
            connection.rollback()
            print(f"Database error during registration: {e}")
            return jsonify({'error': 'An error occurred during registration. Please try again.'}), 500
            
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    # GET request - show registration form
    return render_template('register.html')

# Dashboard routes

@app.route('/Students/dashboard.html')
@app.route('/student/dashboard')
@login_required(['STUDENT'])
def student_dashboard():
    """Enhanced Student dashboard with data"""
    # Get dashboard data
    dashboard_data = get_user_dashboard_data(session['user_id'], 'STUDENT')
    
    # Add user info to dashboard data
    if dashboard_data:
        dashboard_data.update({
            'student_name': session.get('first_name', 'Student'),
            'full_name': session.get('full_name', 'Student'),
            'email': session.get('email', ''),
        })
    
    return render_template('Students/dashboard.html', data=dashboard_data)

@app.route('/Provider/dashboard.html')
@app.route('/provider/dashboard')
@login_required(['PROVIDER'])
def provider_dashboard():
    """Enhanced Provider dashboard with data"""
    # Get dashboard data
    dashboard_data = get_user_dashboard_data(session['user_id'], 'PROVIDER')
    
    # Add user info to dashboard data
    if dashboard_data:
        dashboard_data.update({
            'provider_name': session.get('first_name', 'Provider'),
            'full_name': session.get('full_name', 'Provider'),
            'email': session.get('email', ''),
        })
    
    return render_template('Provider/dashboard.html', data=dashboard_data)

@app.route('/Admin/dashboard.html')
@app.route('/admin/dashboard')
@login_required(['ADMIN'])
def admin_dashboard():
    """Admin dashboard with system management data"""
    # Get admin dashboard data
    dashboard_data = get_admin_dashboard_data()
    
    # Add admin info to dashboard data
    if dashboard_data:
        dashboard_data.update({
            'admin_name': session.get('first_name', 'Administrator'),
            'full_name': session.get('full_name', 'Administrator'),
            'email': session.get('email', ''),
        })
    
    return render_template('Admin/dashboard.html', data=dashboard_data)

# API Routes for AJAX requests

@app.route('/api/auth/status')
def auth_status():
    """Check authentication status"""
    if 'user_id' in session:
        user_type = session['user_type']
        print(f"DEBUG: Auth status check - user_type: '{user_type}'")  # Debug log
        response = {
            'authenticated': True,
            'user': {
                'id': session['user_id'],
                'email': session['email'],
                'user_type': user_type,
                'first_name': session['first_name'],
                'last_name': session['last_name'],
                'full_name': session['full_name']
            }
        }
        print(f"DEBUG: Auth status response: {response}")  # Debug log
        return jsonify(response)
    else:
        print("DEBUG: No user session found")  # Debug log
        return jsonify({'authenticated': False})

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    """API endpoint for login (for AJAX requests)"""
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400
    
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and password are required'}), 400
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Query user by email
        query = """
            SELECT id, email, password_hash, user_type, first_name, last_name, 
                   is_active, is_verified, last_login 
            FROM users 
            WHERE email = %s
        """
        cursor.execute(query, (email,))
        user = cursor.fetchone()
        
        print(f"DEBUG: Login query result for {email}: {user}")  # Debug log
        
        if user and check_password_hash(user['password_hash'], password):
            # Check if user is active
            if not user['is_active']:
                return jsonify({'success': False, 'message': 'Account deactivated'}), 403
            
            # Check if user is verified (approved by admin)
            # Admin accounts are automatically verified, so they can always login
            if not user['is_verified'] and user['user_type'] != 'ADMIN':
                user_type_display = 'student' if user['user_type'] == 'STUDENT' else 'provider'
                return jsonify({
                    'success': False, 
                    'message': f'Your {user_type_display} registration is pending approval. '
                              f'Please wait 2-3 business days for the administrator to review your application. '
                              f'You will be able to login once your account has been approved. '
                              f'Thank you for your patience!',
                    'pending_approval': True
                }), 403
            
            # Update last login
            update_query = "UPDATE users SET last_login = %s WHERE id = %s"
            cursor.execute(update_query, (datetime.now(), user['id']))
            connection.commit()
            
            # Store comprehensive user information in session
            session.permanent = True
            session['user_id'] = user['id']
            session['email'] = user['email']
            session['user_type'] = user['user_type']
            session['first_name'] = user['first_name']
            session['last_name'] = user['last_name']
            session['full_name'] = f"{user['first_name']} {user['last_name']}"
            session['is_verified'] = user['is_verified']
            session['login_time'] = datetime.now().isoformat()
            
            # Determine redirect URL based on user type
            print(f"DEBUG: User type is: '{user['user_type']}'")  # Debug log
            if user['user_type'] == 'STUDENT':
                redirect_url = '/Students/dashboard.html'
                print(f"DEBUG: Redirecting STUDENT to: {redirect_url}")
            elif user['user_type'] == 'PROVIDER':
                redirect_url = '/Provider/dashboard.html'
                print(f"DEBUG: Redirecting PROVIDER to: {redirect_url}")
            elif user['user_type'] == 'ADMIN':
                redirect_url = '/Admin/dashboard.html'
                print(f"DEBUG: Redirecting ADMIN to: {redirect_url}")
            else:
                redirect_url = '/index.html'
                print(f"DEBUG: Unknown user type, redirecting to: {redirect_url}")
            
            print(f"DEBUG: Final redirect_url: {redirect_url}")  # Debug log
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user': {
                    'id': user['id'],
                    'email': user['email'],
                    'user_type': user['user_type'],
                    'first_name': user['first_name'],
                    'last_name': user['last_name'],
                    'full_name': f"{user['first_name']} {user['last_name']}"
                },
                'redirect_url': redirect_url
            })
        else:
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
            
    except Error as e:
        print(f"Database error during API login: {e}")
        return jsonify({'success': False, 'message': 'Database error'}), 500
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Admin API Routes

@app.route('/api/admin/dashboard-stats')
@login_required(['ADMIN'])
def admin_dashboard_stats():
    """Get admin dashboard statistics"""
    try:
        stats = get_admin_dashboard_data()
        return jsonify({'success': True, 'data': stats})
    except Exception as e:
        print(f"Error fetching admin stats: {e}")
        return jsonify({'success': False, 'message': 'Failed to fetch statistics'}), 500

@app.route('/api/admin/profile')
@login_required(['ADMIN'])
def admin_profile():
    """Get admin profile information"""
    return jsonify({
        'success': True,
        'name': session.get('full_name', 'Administrator'),
        'email': session.get('email', 'admin@easescholar.com'),
        'first_name': session.get('first_name', 'Administrator'),
        'last_name': session.get('last_name', '')
    })

@app.route('/api/admin/profile', methods=['POST'])
@login_required(['ADMIN'])
def update_admin_profile():
    """Update admin profile information"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        data = request.get_json()
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        email = data.get('email', '').strip()
        
        # Validate input
        if not first_name or not email:
            return jsonify({'success': False, 'message': 'First name and email are required'}), 400
        
        # Validate email format
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return jsonify({'success': False, 'message': 'Invalid email format'}), 400
        
        user_id = session.get('user_id')
        cursor = connection.cursor()
        
        # Check if email is already used by another user
        cursor.execute("""
            SELECT id FROM users 
            WHERE email = %s AND id != %s
        """, (email, user_id))
        
        if cursor.fetchone():
            return jsonify({'success': False, 'message': 'Email already in use by another account'}), 400
        
        # Update user profile
        cursor.execute("""
            UPDATE users 
            SET first_name = %s, last_name = %s, email = %s
            WHERE id = %s
        """, (first_name, last_name, email, user_id))
        
        connection.commit()
        
        # Update session data
        session['first_name'] = first_name
        session['last_name'] = last_name
        session['email'] = email
        session['full_name'] = f"{first_name} {last_name}".strip()
        
        print(f"✅ Profile updated for admin user {user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'first_name': first_name,
            'last_name': last_name,
            'email': email
        })
        
    except Exception as e:
        print(f"Error updating admin profile: {e}")
        if connection:
            connection.rollback()
        return jsonify({'success': False, 'message': 'Failed to update profile'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/admin/change-password', methods=['POST'])
@login_required(['ADMIN'])
def change_admin_password():
    """Change admin password"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        data = request.get_json()
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        
        # Validate input
        if not current_password or not new_password:
            return jsonify({'success': False, 'message': 'Current and new password are required'}), 400
        
        if len(new_password) < 6:
            return jsonify({'success': False, 'message': 'New password must be at least 6 characters'}), 400
        
        user_id = session.get('user_id')
        cursor = connection.cursor(dictionary=True)
        
        # Get current user data
        cursor.execute("""
            SELECT password FROM users 
            WHERE id = %s
        """, (user_id,))
        
        user = cursor.fetchone()
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        # Verify current password
        if not check_password_hash(user['password'], current_password):
            return jsonify({'success': False, 'message': 'Current password is incorrect'}), 400
        
        # Hash new password
        hashed_password = generate_password_hash(new_password)
        
        # Update password
        cursor.execute("""
            UPDATE users 
            SET password = %s
            WHERE id = %s
        """, (hashed_password, user_id))
        
        connection.commit()
        
        print(f"✅ Password changed for admin user {user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
        })
        
    except Exception as e:
        print(f"Error changing admin password: {e}")
        if connection:
            connection.rollback()
        return jsonify({'success': False, 'message': 'Failed to change password'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/admin/system-settings', methods=['GET'])
@login_required(['ADMIN'])
def get_system_settings():
    """Get system settings"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Check if settings table exists, if not create it
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_settings (
                id INT PRIMARY KEY AUTO_INCREMENT,
                setting_key VARCHAR(100) UNIQUE NOT NULL,
                setting_value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        
        # Get maintenance mode setting
        cursor.execute("""
            SELECT setting_value FROM system_settings 
            WHERE setting_key = 'maintenance_mode'
        """)
        result = cursor.fetchone()
        
        maintenance_mode = False
        if result:
            maintenance_mode = result['setting_value'] == '1' or result['setting_value'] == 'true'
        
        return jsonify({
            'success': True,
            'maintenance_mode': maintenance_mode
        })
        
    except Exception as e:
        print(f"Error getting system settings: {e}")
        return jsonify({'success': False, 'message': 'Failed to get settings'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/admin/system-settings', methods=['POST'])
@login_required(['ADMIN'])
def save_system_settings():
    """Save system settings"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        data = request.get_json()
        maintenance_mode = data.get('maintenance_mode', False)
        
        cursor = connection.cursor()
        
        # Check if settings table exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_settings (
                id INT PRIMARY KEY AUTO_INCREMENT,
                setting_key VARCHAR(100) UNIQUE NOT NULL,
                setting_value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        
        # Insert or update maintenance mode setting
        cursor.execute("""
            INSERT INTO system_settings (setting_key, setting_value)
            VALUES ('maintenance_mode', %s)
            ON DUPLICATE KEY UPDATE setting_value = %s
        """, ('1' if maintenance_mode else '0', '1' if maintenance_mode else '0'))
        
        connection.commit()
        
        print(f"✅ System settings saved: maintenance_mode = {maintenance_mode}")
        
        return jsonify({
            'success': True,
            'message': 'Settings saved successfully',
            'maintenance_mode': maintenance_mode
        })
        
    except Exception as e:
        print(f"Error saving system settings: {e}")
        if connection:
            connection.rollback()
        return jsonify({'success': False, 'message': 'Failed to save settings'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/admin/notifications')
@login_required(['ADMIN'])
def admin_notifications():
    """Get admin notifications"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Get recent user registrations needing approval
        query = """
            SELECT id, email, first_name, last_name, user_type, created_at
            FROM users 
            WHERE is_verified = 0 AND user_type IN ('STUDENT', 'PROVIDER')
            ORDER BY created_at DESC 
            LIMIT 10
        """
        cursor.execute(query)
        pending_users = cursor.fetchall()
        
        notifications = []
        for user in pending_users:
            notifications.append({
                'id': f"approval_{user['id']}",
                'type': 'approval',
                'title': f'New {user["user_type"].lower()} registration requires approval',
                'message': f'{user["first_name"]} {user["last_name"]} ({user["email"]}) has registered and needs verification.',
                'time': f'{(datetime.now() - user["created_at"]).days} days ago' if (datetime.now() - user["created_at"]).days > 0 else 'Today',
                'read': False
            })
        
        return jsonify({
            'success': True,
            'notifications': notifications[:5],  # Limit to 5 most recent
            'unreadCount': len(notifications)
        })
        
    except Exception as e:
        print(f"Error fetching admin notifications: {e}")
        return jsonify({'success': False, 'message': 'Failed to fetch notifications'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/admin/approvals/count')
@login_required(['ADMIN'])
def admin_approvals_count():
    """Get count of pending approvals"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE is_verified = 0 AND user_type IN ('STUDENT', 'PROVIDER')")
        result = cursor.fetchone()
        count = result[0] if result else 0
        
        return jsonify({'success': True, 'count': count})
        
    except Exception as e:
        print(f"Error fetching approvals count: {e}")
        return jsonify({'success': False, 'count': 0})
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/admin/pending-approvals')
@login_required(['ADMIN'])
def get_pending_approvals():
    """Get list of pending user approvals with details"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Get pending students with their profile data
        student_query = """
            SELECT u.id, u.email, u.first_name, u.last_name, u.phone_number, 
                   u.user_type, u.created_at,
                   s.student_number, s.school_name, s.course, s.year_level, s.gpa,
                   s.expected_graduation_date, s.cor_document, s.coe_document, s.transcript_document
            FROM users u
            LEFT JOIN students s ON u.id = s.user_id
            WHERE u.is_verified = 0 AND u.user_type = 'STUDENT'
            ORDER BY u.created_at DESC
        """
        cursor.execute(student_query)
        students = cursor.fetchall()
        
        # Get pending providers with their profile data
        provider_query = """
            SELECT u.id, u.email, u.first_name, u.last_name, u.phone_number,
                   u.user_type, u.created_at,
                   p.organization_name, p.organization_type, p.website, p.description,
                   p.business_registration_document
            FROM users u
            LEFT JOIN providers p ON u.id = p.user_id
            WHERE u.is_verified = 0 AND u.user_type = 'PROVIDER'
            ORDER BY u.created_at DESC
        """
        cursor.execute(provider_query)
        providers = cursor.fetchall()
        
        # Combine and format results
        pending_users = []
        
        for student in students:
            pending_users.append({
                'id': student['id'],
                'email': student['email'],
                'first_name': student['first_name'],
                'last_name': student['last_name'],
                'full_name': f"{student['first_name']} {student['last_name']}",
                'phone_number': student['phone_number'],
                'user_type': student['user_type'],
                'created_at': student['created_at'].isoformat() if student['created_at'] else None,
                'student_number': student.get('student_number'),
                'school_name': student.get('school_name'),
                'course': student.get('course'),
                'year_level': student.get('year_level'),
                'gpa': float(student['gpa']) if student.get('gpa') else None,
                'expected_graduation_date': student.get('expected_graduation_date').isoformat() if student.get('expected_graduation_date') else None,
                'documents': {
                    'cor': student.get('cor_document'),
                    'coe': student.get('coe_document'),
                    'transcript': student.get('transcript_document')
                }
            })
        
        for provider in providers:
            pending_users.append({
                'id': provider['id'],
                'email': provider['email'],
                'first_name': provider['first_name'],
                'last_name': provider['last_name'],
                'full_name': f"{provider['first_name']} {provider['last_name']}",
                'phone_number': provider['phone_number'],
                'user_type': provider['user_type'],
                'created_at': provider['created_at'].isoformat() if provider['created_at'] else None,
                'organization_name': provider.get('organization_name'),
                'organization_type': provider.get('organization_type'),
                'website': provider.get('website'),
                'description': provider.get('description'),
                'documents': {
                    'business_registration': provider.get('business_registration_document')
                }
            })
        
        return jsonify({
            'success': True,
            'pending_users': pending_users,
            'total_count': len(pending_users)
        })
        
    except Exception as e:
        print(f"Error fetching pending approvals: {e}")
        return jsonify({'success': False, 'message': 'Failed to fetch pending approvals'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/admin/approve-user/<int:user_id>', methods=['POST'])
@login_required(['ADMIN'])
def approve_user(user_id):
    """Approve a pending user registration"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Get user details
        cursor.execute("SELECT id, email, user_type FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        # Update user verification status
        update_query = """
            UPDATE users 
            SET is_verified = 1, updated_at = %s 
            WHERE id = %s
        """
        cursor.execute(update_query, (datetime.now(), user_id))
        
        # If provider, also update provider verification
        if user['user_type'] == 'PROVIDER':
            cursor.execute("UPDATE providers SET is_verified = 1 WHERE user_id = %s", (user_id,))
        
        connection.commit()
        
        # TODO: Send approval email notification
        
        return jsonify({
            'success': True,
            'message': f'{user["user_type"].capitalize()} approved successfully',
            'user_id': user_id
        })
        
    except Exception as e:
        connection.rollback()
        print(f"Error approving user: {e}")
        return jsonify({'success': False, 'message': 'Failed to approve user'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/admin/reject-user/<int:user_id>', methods=['POST'])
@login_required(['ADMIN'])
def reject_user(user_id):
    """Reject a pending user registration"""
    data = request.get_json() or {}
    reason = data.get('reason', 'No reason provided')
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Get user details
        cursor.execute("SELECT id, email, user_type FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        # Option 1: Delete the user (hard delete)
        # Delete associated records first due to foreign key constraints
        if user['user_type'] == 'STUDENT':
            cursor.execute("DELETE FROM students WHERE user_id = %s", (user_id,))
        elif user['user_type'] == 'PROVIDER':
            cursor.execute("DELETE FROM providers WHERE user_id = %s", (user_id,))
        
        # Delete user
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        
        connection.commit()
        
        # TODO: Send rejection email with reason
        
        return jsonify({
            'success': True,
            'message': f'{user["user_type"].capitalize()} registration rejected',
            'user_id': user_id
        })
        
    except Exception as e:
        connection.rollback()
        print(f"Error rejecting user: {e}")
        return jsonify({'success': False, 'message': 'Failed to reject user'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/admin/users')
@login_required(['ADMIN'])
def get_all_users():
    """Get all users with filtering options"""
    user_type_filter = request.args.get('type', 'ALL')  # ALL, STUDENT, PROVIDER
    status_filter = request.args.get('status', 'ALL')   # ALL, VERIFIED, PENDING, INACTIVE
    search_query = request.args.get('search', '')
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Build dynamic query based on filters
        query = """
            SELECT u.id, u.email, u.first_name, u.last_name, u.phone_number,
                   u.user_type, u.is_active, u.is_verified, u.created_at, u.last_login,
                   CASE 
                       WHEN u.user_type = 'STUDENT' THEN s.school_name
                       WHEN u.user_type = 'PROVIDER' THEN p.organization_name
                       ELSE NULL
                   END as institution_name
            FROM users u
            LEFT JOIN students s ON u.id = s.user_id AND u.user_type = 'STUDENT'
            LEFT JOIN providers p ON u.id = p.user_id AND u.user_type = 'PROVIDER'
            WHERE 1=1
        """
        params = []
        
        # Apply user type filter
        if user_type_filter != 'ALL':
            query += " AND u.user_type = %s"
            params.append(user_type_filter)
        else:
            # Exclude admin users from listing
            query += " AND u.user_type IN ('STUDENT', 'PROVIDER')"
        
        # Apply status filter
        if status_filter == 'VERIFIED':
            query += " AND u.is_verified = 1"
        elif status_filter == 'PENDING':
            query += " AND u.is_verified = 0"
        elif status_filter == 'INACTIVE':
            query += " AND u.is_active = 0"
        
        # Apply search filter
        if search_query:
            query += """ AND (u.email LIKE %s OR u.first_name LIKE %s OR u.last_name LIKE %s 
                        OR s.school_name LIKE %s OR p.organization_name LIKE %s)"""
            search_pattern = f"%{search_query}%"
            params.extend([search_pattern] * 5)
        
        query += " ORDER BY u.created_at DESC"
        
        cursor.execute(query, params)
        users = cursor.fetchall()
        
        # Format results
        formatted_users = []
        for user in users:
            formatted_users.append({
                'id': user['id'],
                'email': user['email'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'full_name': f"{user['first_name']} {user['last_name']}",
                'phone_number': user['phone_number'],
                'user_type': user['user_type'],
                'is_active': bool(user['is_active']),
                'is_verified': bool(user['is_verified']),
                'institution_name': user['institution_name'],
                'created_at': user['created_at'].isoformat() if user['created_at'] else None,
                'last_login': user['last_login'].isoformat() if user['last_login'] else None
            })
        
        return jsonify({
            'success': True,
            'users': formatted_users,
            'total_count': len(formatted_users)
        })
        
    except Exception as e:
        print(f"Error fetching users: {e}")
        return jsonify({'success': False, 'message': 'Failed to fetch users'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/admin/user/<int:user_id>/toggle-active', methods=['POST'])
@login_required(['ADMIN'])
def toggle_user_active(user_id):
    """Toggle user active status"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Get current status
        cursor.execute("SELECT id, is_active FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        # Toggle status
        new_status = not bool(user['is_active'])
        cursor.execute("UPDATE users SET is_active = %s, updated_at = %s WHERE id = %s", 
                      (new_status, datetime.now(), user_id))
        connection.commit()
        
        return jsonify({
            'success': True,
            'message': f'User {"activated" if new_status else "deactivated"} successfully',
            'is_active': new_status
        })
        
    except Exception as e:
        connection.rollback()
        print(f"Error toggling user status: {e}")
        return jsonify({'success': False, 'message': 'Failed to update user status'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/admin/user/<int:user_id>/details')
@login_required(['ADMIN'])
def get_user_details(user_id):
    """Get detailed information about a specific user"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Get user basic info
        cursor.execute("""
            SELECT id, email, first_name, last_name, phone_number, user_type,
                   is_active, is_verified, created_at, updated_at, last_login
            FROM users WHERE id = %s
        """, (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        user_details = {
            'id': user['id'],
            'email': user['email'],
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'full_name': f"{user['first_name']} {user['last_name']}",
            'phone_number': user['phone_number'],
            'user_type': user['user_type'],
            'is_active': bool(user['is_active']),
            'is_verified': bool(user['is_verified']),
            'created_at': user['created_at'].isoformat() if user['created_at'] else None,
            'updated_at': user['updated_at'].isoformat() if user['updated_at'] else None,
            'last_login': user['last_login'].isoformat() if user['last_login'] else None
        }
        
        # Get type-specific details
        if user['user_type'] == 'STUDENT':
            cursor.execute("""
                SELECT student_number, school_name, course, year_level, gpa,
                       expected_graduation_date, cor_document, coe_document, transcript_document
                FROM students WHERE user_id = %s
            """, (user_id,))
            student_data = cursor.fetchone()
            if student_data:
                user_details['profile'] = {
                    'student_number': student_data['student_number'],
                    'school_name': student_data['school_name'],
                    'course': student_data['course'],
                    'year_level': student_data['year_level'],
                    'gpa': float(student_data['gpa']) if student_data['gpa'] else None,
                    'expected_graduation_date': student_data['expected_graduation_date'].isoformat() if student_data['expected_graduation_date'] else None,
                    'documents': {
                        'cor': student_data['cor_document'],
                        'coe': student_data['coe_document'],
                        'transcript': student_data['transcript_document']
                    }
                }
        
        elif user['user_type'] == 'PROVIDER':
            cursor.execute("""
                SELECT organization_name, organization_type, website, description,
                       business_registration_document, is_verified
                FROM providers WHERE user_id = %s
            """, (user_id,))
            provider_data = cursor.fetchone()
            if provider_data:
                user_details['profile'] = {
                    'organization_name': provider_data['organization_name'],
                    'organization_type': provider_data['organization_type'],
                    'website': provider_data['website'],
                    'description': provider_data['description'],
                    'is_verified': bool(provider_data['is_verified']),
                    'documents': {
                        'business_registration': provider_data['business_registration_document']
                    }
                }
        
        return jsonify({
            'success': True,
            'user': user_details
        })
        
    except Exception as e:
        print(f"Error fetching user details: {e}")
        return jsonify({'success': False, 'message': 'Failed to fetch user details'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# ============================================================================
# NEW ADMIN API ENDPOINTS FOR DETAILED MANAGEMENT
# ============================================================================

@app.route('/api/admin/students')
@login_required(['ADMIN'])
def get_all_students():
    """Get all students with their details"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        query = """
            SELECT u.id as user_id, u.email, u.first_name, u.last_name, u.phone_number,
                   u.is_active, u.is_verified, u.created_at, u.last_login,
                   s.student_number as student_id, s.school_name, s.course as program, 
                   s.year_level, s.gpa, s.date_of_birth, s.gender,
                   s.cor_document, s.coe_document
            FROM users u
            LEFT JOIN students s ON u.id = s.user_id
            WHERE u.user_type = 'STUDENT'
            ORDER BY u.created_at DESC
        """
        cursor.execute(query)
        students = cursor.fetchall()
        
        students_list = []
        for student in students:
            students_list.append({
                'user_id': student['user_id'],
                'email': student['email'],
                'first_name': student['first_name'],
                'last_name': student['last_name'],
                'full_name': f"{student['first_name']} {student['last_name']}",
                'phone_number': student['phone_number'],
                'student_id': student['student_id'],
                'school_name': student['school_name'],
                'program': student['program'],
                'year_level': student['year_level'],
                'gpa': float(student['gpa']) if student['gpa'] else None,
                'date_of_birth': student['date_of_birth'].isoformat() if student.get('date_of_birth') else None,
                'gender': student.get('gender'),
                'is_active': bool(student['is_active']),
                'is_verified': bool(student['is_verified']),
                'created_at': student['created_at'].isoformat() if student['created_at'] else None,
                'last_login': student['last_login'].isoformat() if student.get('last_login') else None,
                'cor_document': student.get('cor_document'),
                'coe_document': student.get('coe_document')
            })
        
        return jsonify({
            'success': True,
            'students': students_list
        })
        
    except Exception as e:
        print(f"Error fetching students: {e}")
        return jsonify({'success': False, 'message': 'Failed to fetch students'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/admin/providers')
@login_required(['ADMIN'])
def get_all_providers():
    """Get all providers with their details"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        query = """
            SELECT u.id as user_id, u.email, u.first_name, u.last_name, u.phone_number,
                   u.is_active, u.is_verified, u.created_at, u.last_login,
                   p.organization_name, p.organization_type, p.website, p.address,
                   p.description, p.business_registration_document,
                   (SELECT COUNT(*) FROM scholarships WHERE provider_id = u.id) as scholarship_count
            FROM users u
            LEFT JOIN providers p ON u.id = p.user_id
            WHERE u.user_type = 'PROVIDER'
            ORDER BY u.created_at DESC
        """
        cursor.execute(query)
        providers = cursor.fetchall()
        
        providers_list = []
        for provider in providers:
            providers_list.append({
                'user_id': provider['user_id'],
                'email': provider['email'],
                'first_name': provider['first_name'],
                'last_name': provider['last_name'],
                'full_name': f"{provider['first_name']} {provider['last_name']}",
                'phone_number': provider['phone_number'],
                'organization_name': provider['organization_name'],
                'organization_type': provider['organization_type'],
                'website': provider['website'],
                'address': provider['address'],
                'description': provider['description'],
                'position': provider.get('position'),
                'business_registration': provider.get('business_registration_document'),
                'is_active': bool(provider['is_active']),
                'is_verified': bool(provider['is_verified']),
                'created_at': provider['created_at'].isoformat() if provider['created_at'] else None,
                'last_login': provider['last_login'].isoformat() if provider.get('last_login') else None,
                'scholarship_count': provider['scholarship_count']
            })
        
        return jsonify({
            'success': True,
            'providers': providers_list
        })
        
    except Exception as e:
        print(f"Error fetching providers: {e}")
        return jsonify({'success': False, 'message': 'Failed to fetch providers'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/admin/scholarships')
@login_required(['ADMIN'])
def get_all_scholarships():
    """Get all scholarships with provider details"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        query = """
            SELECT s.id, s.title, s.description, s.scholarship_type, s.amount, s.currency,
                   s.eligibility_criteria, s.required_documents, s.application_deadline,
                   s.scholarship_duration, s.available_slots, s.is_active, s.created_at,
                   CONCAT(u.first_name, ' ', u.last_name) as provider_name,
                   p.organization_name,
                   (SELECT COUNT(*) FROM applications WHERE scholarship_id = s.id) as application_count
            FROM scholarships s
            INNER JOIN users u ON s.provider_id = u.id
            LEFT JOIN providers p ON u.id = p.user_id
            ORDER BY s.created_at DESC
        """
        cursor.execute(query)
        scholarships = cursor.fetchall()
        
        scholarships_list = []
        for scholarship in scholarships:
            scholarships_list.append({
                'id': scholarship['id'],
                'title': scholarship['title'],
                'description': scholarship['description'],
                'scholarship_type': scholarship['scholarship_type'],
                'amount': float(scholarship['amount']),
                'currency': scholarship['currency'] or 'PHP',
                'eligibility_criteria': scholarship['eligibility_criteria'],
                'required_documents': scholarship['required_documents'],
                'application_deadline': scholarship['application_deadline'].isoformat() if scholarship.get('application_deadline') else None,
                'scholarship_duration': scholarship['scholarship_duration'],
                'available_slots': scholarship['available_slots'],
                'is_active': bool(scholarship['is_active']),
                'created_at': scholarship['created_at'].isoformat() if scholarship['created_at'] else None,
                'provider_name': scholarship['provider_name'],
                'organization_name': scholarship.get('organization_name'),
                'application_count': scholarship['application_count']
            })
        
        return jsonify({
            'success': True,
            'scholarships': scholarships_list
        })
        
    except Exception as e:
        print(f"Error fetching scholarships: {e}")
        return jsonify({'success': False, 'message': 'Failed to fetch scholarships'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/admin/applications')
@login_required(['ADMIN'])
def get_all_applications():
    """Get all scholarship applications"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Fixed query: Use LEFT JOIN to get all applications even if related data is missing
        # student_id in applications table refers to students.id, not users.id
        query = """
            SELECT a.id, a.status, a.cover_letter, a.additional_info,
                   a.submitted_at, a.reviewed_at, a.reviewer_notes,
                   CONCAT(COALESCE(u.first_name, 'Unknown'), ' ', COALESCE(u.last_name, 'Student')) as student_name,
                   COALESCE(u.email, 'N/A') as student_email,
                   COALESCE(s.title, 'N/A') as scholarship_title,
                   CONCAT(COALESCE(p_user.first_name, 'Unknown'), ' ', COALESCE(p_user.last_name, 'Provider')) as provider_name
            FROM applications a
            LEFT JOIN students st ON a.student_id = st.id
            LEFT JOIN users u ON st.user_id = u.id
            LEFT JOIN scholarships s ON a.scholarship_id = s.id
            LEFT JOIN providers p ON s.provider_id = p.id
            LEFT JOIN users p_user ON p.user_id = p_user.id
            ORDER BY a.submitted_at DESC
        """
        cursor.execute(query)
        applications = cursor.fetchall()
        
        print(f"📋 Fetched {len(applications)} applications from database")
        
        applications_list = []
        for app in applications:
            applications_list.append({
                'id': app['id'],
                'student_name': app['student_name'],
                'student_email': app['student_email'],
                'scholarship_title': app['scholarship_title'],
                'provider_name': app['provider_name'],
                'status': app['status'],
                'cover_letter': app['cover_letter'],
                'additional_info': app['additional_info'],
                'submitted_at': app['submitted_at'].isoformat() if app['submitted_at'] else None,
                'reviewed_at': app['reviewed_at'].isoformat() if app.get('reviewed_at') else None,
                'reviewer_notes': app['reviewer_notes']
            })
        
        print(f"✅ Returning {len(applications_list)} applications to client")
        print(f"   Status breakdown: " + 
              f"APPROVED={sum(1 for a in applications_list if a['status'] == 'APPROVED')}, " +
              f"REJECTED={sum(1 for a in applications_list if a['status'] == 'REJECTED')}, " +
              f"PENDING={sum(1 for a in applications_list if a['status'] == 'PENDING')}, " +
              f"UNDER_REVIEW={sum(1 for a in applications_list if a['status'] == 'UNDER_REVIEW')}")
        
        response = jsonify({
            'success': True,
            'applications': applications_list
        })
        
        # Add cache control headers to prevent caching
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response
        
    except Exception as e:
        print(f"❌ Error fetching applications: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'Failed to fetch applications'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/admin/toggle-user-status', methods=['POST'])
@login_required(['ADMIN'])
def toggle_user_status():
    """Toggle user active status"""
    data = request.get_json()
    user_id = data.get('user_id')
    is_active = data.get('is_active')
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor()
        cursor.execute("UPDATE users SET is_active = %s WHERE id = %s", (is_active, user_id))
        connection.commit()
        
        return jsonify({
            'success': True,
            'message': 'User status updated successfully'
        })
        
    except Exception as e:
        connection.rollback()
        print(f"Error toggling user status: {e}")
        return jsonify({'success': False, 'message': 'Failed to update user status'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/admin/toggle-scholarship-status', methods=['POST'])
@login_required(['ADMIN'])
def toggle_scholarship_status():
    """Toggle scholarship active status"""
    data = request.get_json()
    scholarship_id = data.get('scholarship_id')
    is_active = data.get('is_active')
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor()
        cursor.execute("UPDATE scholarships SET is_active = %s WHERE id = %s", (is_active, scholarship_id))
        connection.commit()
        
        return jsonify({
            'success': True,
            'message': 'Scholarship status updated successfully'
        })
        
    except Exception as e:
        connection.rollback()
        print(f"Error toggling scholarship status: {e}")
        return jsonify({'success': False, 'message': 'Failed to update scholarship status'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# ============================================================================
# END OF NEW ADMIN API ENDPOINTS
# ============================================================================

@app.route('/forgot-password', methods=['GET', 'POST'])
@app.route('/forgot-password.html', methods=['GET', 'POST'])
def forgot_password():
    """Handle forgot password requests"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        
        if not email:
            flash('Please enter your email address.', 'error')
            return render_template('forgot-password.html', error='Please enter your email address.')
        
        connection = get_db_connection()
        if not connection:
            flash('Database connection failed. Please try again later.', 'error')
            return render_template('forgot-password.html', error='Database connection failed.')
        
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Check if user exists
            cursor.execute("SELECT id, email, first_name, last_name FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            
            if user:
                # Generate secure reset token
                reset_token = secrets.token_urlsafe(32)
                expires_at = datetime.now() + timedelta(hours=1)
                
                # Store reset token in database
                cursor.execute("""
                    INSERT INTO password_reset_tokens (user_id, email, token, expires_at, used, created_at)
                    VALUES (%s, %s, %s, %s, 0, NOW())
                """, (user['id'], email, reset_token, expires_at))
                connection.commit()
                
                # Create reset link
                reset_link = f"{request.url_root}reset-password/{reset_token}"
                
                # Send email
                try:
                    msg = Message(
                        subject='EASESCHOLAR - Password Reset Request',
                        recipients=[email]
                    )
                    
                    # HTML email body
                    msg.html = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <style>
                            body {{ font-family: 'Inter', Arial, sans-serif; line-height: 1.6; color: #333; }}
                            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                       color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                            .content {{ background: #ffffff; padding: 30px; border: 1px solid #e5e7eb; 
                                        border-top: none; border-radius: 0 0 10px 10px; }}
                            .button {{ display: inline-block; background: #667eea; color: white !important; 
                                      padding: 14px 28px; text-decoration: none; border-radius: 8px; 
                                      font-weight: 600; margin: 20px 0; }}
                            .button:hover {{ background: #5568d3; }}
                            .footer {{ text-align: center; margin-top: 30px; color: #6b7280; font-size: 14px; }}
                            .warning {{ background: #fef3c7; border-left: 4px solid #f59e0b; 
                                       padding: 15px; margin: 20px 0; border-radius: 4px; }}
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <div class="header">
                                <h1 style="margin: 0; font-size: 28px;">🔐 Password Reset Request</h1>
                            </div>
                            <div class="content">
                                <p>Hello <strong>{user['first_name']} {user['last_name']}</strong>,</p>
                                
                                <p>We received a request to reset your password for your EASESCHOLAR account. 
                                   Click the button below to create a new password:</p>
                                
                                <div style="text-align: center;">
                                    <a href="{reset_link}" class="button">Reset My Password</a>
                                </div>
                                
                                <p>Or copy and paste this link into your browser:</p>
                                <p style="background: #f3f4f6; padding: 12px; border-radius: 6px; 
                                          word-break: break-all; font-size: 14px;">
                                    {reset_link}
                                </p>
                                
                                <div class="warning">
                                    <p style="margin: 0;"><strong>⚠️ Important Security Information:</strong></p>
                                    <ul style="margin: 10px 0 0 0;">
                                        <li>This link will expire in <strong>1 hour</strong></li>
                                        <li>If you didn't request this reset, please ignore this email</li>
                                        <li>Never share this link with anyone</li>
                                    </ul>
                                </div>
                                
                                <p style="margin-top: 30px;">Best regards,<br>
                                   <strong>The EASESCHOLAR Team</strong></p>
                            </div>
                            <div class="footer">
                                <p>This is an automated message from EASESCHOLAR Scholarship Management Platform</p>
                                <p>&copy; 2025 EASESCHOLAR. All rights reserved.</p>
                            </div>
                        </div>
                    </body>
                    </html>
                    """
                    
                    # Plain text alternative
                    msg.body = f"""
                    EASESCHOLAR - Password Reset Request
                    
                    Hello {user['first_name']} {user['last_name']},
                    
                    We received a request to reset your password for your EASESCHOLAR account.
                    
                    Click or copy this link to reset your password:
                    {reset_link}
                    
                    IMPORTANT:
                    - This link will expire in 1 hour
                    - If you didn't request this reset, please ignore this email
                    - Never share this link with anyone
                    
                    Best regards,
                    The EASESCHOLAR Team
                    
                    ---
                    This is an automated message from EASESCHOLAR Scholarship Management Platform
                    © 2025 EASESCHOLAR. All rights reserved.
                    """
                    
                    mail.send(msg)
                    print(f"Password reset email sent successfully to {email}")
                    
                except Exception as email_error:
                    print(f"Error sending email: {email_error}")
                    # Don't reveal email sending failure to user for security
                    pass
                
            # Always show same message regardless of whether email exists (security best practice)
            flash('If an account with this email exists, you will receive a password reset link shortly.', 'success')
            return render_template('forgot-password.html', 
                                 success='If an account with this email exists, you will receive a password reset link shortly. Please check your inbox and spam folder.')
            
        except Exception as e:
            print(f"Error during forgot password: {e}")
            flash('An error occurred. Please try again.', 'error')
            return render_template('forgot-password.html', error='An error occurred. Please try again.')
            
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    # GET request - show forgot password form
    return render_template('forgot-password.html')

# ============================================================================
# PASSWORD RESET API ENDPOINTS
# ============================================================================

@app.route('/reset-password/<token>')
def reset_password_page(token):
    """Display password reset page"""
    return render_template('reset-password.html')

@app.route('/api/verify-reset-token/<token>', methods=['GET'])
def verify_reset_token(token):
    """Verify if a password reset token is valid"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'valid': False, 'message': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Check if token exists and is not expired or used
        cursor.execute("""
            SELECT id, user_id, email, expires_at, used
            FROM password_reset_tokens
            WHERE token = %s
        """, (token,))
        
        token_data = cursor.fetchone()
        
        if not token_data:
            return jsonify({'valid': False, 'message': 'Invalid token'}), 400
        
        if token_data['used']:
            return jsonify({'valid': False, 'message': 'Token has already been used'}), 400
        
        if datetime.now() > token_data['expires_at']:
            return jsonify({'valid': False, 'message': 'Token has expired'}), 400
        
        return jsonify({'valid': True, 'message': 'Token is valid'})
        
    except Exception as e:
        print(f"Error verifying reset token: {e}")
        return jsonify({'valid': False, 'message': 'Verification failed'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/reset-password', methods=['POST'])
def reset_password_api():
    """Reset password using valid token"""
    data = request.get_json()
    token = data.get('token', '').strip()
    new_password = data.get('new_password', '').strip()
    
    # Validation
    if not token or not new_password:
        return jsonify({'success': False, 'message': 'Token and password are required'}), 400
    
    if len(new_password) < 6:
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters long'}), 400
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Verify token
        cursor.execute("""
            SELECT id, user_id, email, expires_at, used
            FROM password_reset_tokens
            WHERE token = %s
        """, (token,))
        
        token_data = cursor.fetchone()
        
        if not token_data:
            return jsonify({'success': False, 'message': 'Invalid reset token'}), 400
        
        if token_data['used']:
            return jsonify({'success': False, 'message': 'This reset link has already been used'}), 400
        
        if datetime.now() > token_data['expires_at']:
            return jsonify({'success': False, 'message': 'This reset link has expired. Please request a new one.'}), 400
        
        # Hash new password using the existing password hashing function
        password_hash = generate_password_hash(new_password)
        
        # Update user password
        cursor.execute("""
            UPDATE users
            SET password_hash = %s, updated_at = NOW()
            WHERE id = %s
        """, (password_hash, token_data['user_id']))
        
        # Mark token as used
        cursor.execute("""
            UPDATE password_reset_tokens
            SET used = 1
            WHERE id = %s
        """, (token_data['id'],))
        
        connection.commit()
        
        print(f"Password reset successful for user {token_data['user_id']} ({token_data['email']})")
        
        return jsonify({
            'success': True,
            'message': 'Password has been reset successfully. You can now log in with your new password.'
        })
        
    except Exception as e:
        print(f"Error resetting password: {e}")
        connection.rollback()
        return jsonify({'success': False, 'message': 'Failed to reset password. Please try again.'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# ============================================================================
# END OF PASSWORD RESET API ENDPOINTS
# ============================================================================

# Error handlers

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('404.html'), 500

# Context processors for templates

@app.context_processor
def inject_user():
    """Inject user data into all templates"""
    if 'user_id' in session:
        return {
            'current_user': {
                'id': session['user_id'],
                'email': session['email'],
                'user_type': session['user_type'],
                'first_name': session['first_name'],
                'last_name': session['last_name'],
                'full_name': session['full_name']
            }
        }
    return {}

# Development utilities

@app.route('/api/user/profile')
def get_user_profile():
    """Get current user profile information"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Get user information
        query = """
            SELECT u.id, u.email, u.user_type, u.first_name, u.last_name, 
                   u.phone_number, u.is_verified, u.created_at
            FROM users u
            WHERE u.id = %s
        """
        cursor.execute(query, (session['user_id'],))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'success': True,
            'user': user
        })
        
    except Exception as e:
        print(f"Error fetching user profile: {e}")
        return jsonify({'error': 'Database error'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/dashboard/data')
def get_dashboard_data():
    """API endpoint to get dashboard data"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_type = session.get('user_type')
    dashboard_data = get_user_dashboard_data(session['user_id'], user_type)
    
    if dashboard_data is None:
        return jsonify({'error': 'Failed to fetch dashboard data'}), 500
    
    return jsonify({
        'success': True,
        'data': dashboard_data,
        'user_type': user_type
    })

@app.route('/create-admin-user')
def create_admin_user():
    """Utility route to create admin user manually"""
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Check if admin user exists
            cursor.execute("SELECT * FROM users WHERE email = 'admin@gmail.com'")
            admin = cursor.fetchone()
            
            if admin:
                return "Admin user already exists! Email: admin@gmail.com, Password: 12345"
            
            # Create admin user
            password = "12345"
            hashed_password = generate_password_hash(password)
            now = datetime.now()
            
            insert_query = """
            INSERT INTO users (email, password_hash, user_type, first_name, last_name, 
                             phone_number, is_active, is_verified, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                'admin@gmail.com',
                hashed_password,
                'ADMIN',
                'System',
                'Administrator',
                '09123456789',
                1,
                1,
                now,
                now
            )
            
            cursor.execute(insert_query, values)
            connection.commit()
            message = "Admin user created successfully!<br>Email: admin@gmail.com<br>Password: 12345"
            
        except Exception as e:
            message = f"Error creating admin user: {e}"
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
        
        return message
    
    return "Database connection failed"

@app.route('/api/student/scholarships')
def get_available_scholarships():
    """Get available scholarships for students"""
    if 'user_id' not in session or session.get('user_type') != 'STUDENT':
        return jsonify({'error': 'Unauthorized'}), 401
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Get active scholarships that are still accepting applications
        query = """
        SELECT s.id, s.title, s.description, s.amount, s.application_deadline,
               s.required_documents, s.eligibility_criteria, s.scholarship_type,
               s.available_slots, s.is_active, s.created_at,
               p.organization_name as provider_name, p.id as provider_id,
               CASE WHEN s.application_deadline >= NOW() THEN 'open' ELSE 'closed' END as application_status,
               (SELECT COUNT(*) FROM applications WHERE scholarship_id = s.id) as application_count
        FROM scholarships s
        JOIN providers p ON s.provider_id = p.id
        WHERE s.is_active = 1
        ORDER BY s.created_at DESC
        """
        
        cursor.execute(query)
        scholarships = cursor.fetchall()
        
        # Convert datetime objects to strings
        for scholarship in scholarships:
            for key, value in scholarship.items():
                if hasattr(value, 'strftime'):
                    scholarship[key] = value.strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({
            'success': True,
            'scholarships': scholarships
        })
        
    except Exception as e:
        print(f"Error fetching scholarships: {e}")
        return jsonify({'error': 'Database error'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/student/applications')
@login_required(['STUDENT'])
def get_student_applications():
    """Get all applications for the current student with detailed information"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        user_id = session.get('user_id')
        cursor = connection.cursor(dictionary=True)
        
        # Get student ID
        cursor.execute("SELECT id FROM students WHERE user_id = %s", (user_id,))
        student = cursor.fetchone()
        
        if not student:
            return jsonify({'success': False, 'message': 'Student profile not found'}), 404
        
        student_id = student['id']
        
        # Get all applications with scholarship details
        query = """
        SELECT 
            a.id,
            a.status,
            a.cover_letter as essay,
            a.additional_info,
            a.submitted_at,
            a.reviewed_at,
            a.reviewer_notes,
            a.created_at,
            s.id as scholarship_id,
            s.title as scholarship_title,
            s.description,
            s.amount,
            s.scholarship_type,
            s.application_deadline,
            p.organization_name as provider_name,
            (SELECT COUNT(*) FROM application_documents WHERE application_id = a.id) as document_count
        FROM applications a
        JOIN scholarships s ON a.scholarship_id = s.id
        JOIN providers p ON s.provider_id = p.id
        WHERE a.student_id = %s
        ORDER BY a.created_at DESC
        """
        
        cursor.execute(query, (student_id,))
        applications = cursor.fetchall()
        
        # Serialize datetime objects
        for app in applications:
            if app.get('submitted_at'):
                app['submitted_at'] = app['submitted_at'].strftime('%Y-%m-%d %H:%M:%S')
            if app.get('reviewed_at'):
                app['reviewed_at'] = app['reviewed_at'].strftime('%Y-%m-%d %H:%M:%S')
            if app.get('created_at'):
                app['created_at'] = app['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            if app.get('application_deadline'):
                app['application_deadline'] = app['application_deadline'].strftime('%Y-%m-%d')
        
        # Get statistics
        stats_query = """
        SELECT 
            COUNT(*) as total_applications,
            SUM(CASE WHEN status = 'PENDING' THEN 1 ELSE 0 END) as pending,
            SUM(CASE WHEN status = 'UNDER_REVIEW' THEN 1 ELSE 0 END) as under_review,
            SUM(CASE WHEN status = 'APPROVED' THEN 1 ELSE 0 END) as approved,
            SUM(CASE WHEN status = 'REJECTED' THEN 1 ELSE 0 END) as rejected
        FROM applications
        WHERE student_id = %s
        """
        
        cursor.execute(stats_query, (student_id,))
        stats = cursor.fetchone()
        
        print(f"[DEBUG] Found {len(applications)} applications for student {student_id}")
        
        return jsonify({
            'success': True,
            'applications': applications,
            'stats': stats
        })
        
    except Exception as e:
        print(f"Error fetching student applications: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'Failed to fetch applications'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/student/scholarship/<int:scholarship_id>')
@login_required(['STUDENT'])
def get_scholarship_details(scholarship_id):
    """Get detailed information about a specific scholarship"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Get scholarship details
        query = """
        SELECT s.id, s.title, s.description, s.amount, s.application_deadline,
               s.required_documents, s.eligibility_criteria, s.scholarship_type,
               s.available_slots, s.is_active, s.created_at,
               p.organization_name, p.organization_type, p.website, p.contact_person,
               p.address, p.city, p.state,
               u.phone_number as provider_phone,
               (SELECT COUNT(*) FROM applications WHERE scholarship_id = s.id) as application_count,
               CASE WHEN s.application_deadline >= NOW() THEN 'open' ELSE 'closed' END as application_status
        FROM scholarships s
        JOIN providers p ON s.provider_id = p.id
        JOIN users u ON p.user_id = u.id
        WHERE s.id = %s AND s.is_active = 1
        """
        
        cursor.execute(query, (scholarship_id,))
        scholarship = cursor.fetchone()
        
        if not scholarship:
            return jsonify({'success': False, 'message': 'Scholarship not found'}), 404
        
        # Check if student has already applied
        user_id = session.get('user_id')
        cursor.execute("SELECT id FROM students WHERE user_id = %s", (user_id,))
        student = cursor.fetchone()
        
        if student:
            cursor.execute("""
                SELECT id, status FROM applications 
                WHERE student_id = %s AND scholarship_id = %s
            """, (student['id'], scholarship_id))
            existing_application = cursor.fetchone()
            scholarship['has_applied'] = existing_application is not None
            scholarship['application_status_student'] = existing_application['status'] if existing_application else None
        else:
            scholarship['has_applied'] = False
            scholarship['application_status_student'] = None
        
        # Convert datetime objects to strings
        for key, value in scholarship.items():
            if hasattr(value, 'strftime'):
                scholarship[key] = value.strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({'success': True, 'scholarship': scholarship})
        
    except Exception as e:
        print(f"Error fetching scholarship details: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'Failed to fetch scholarship details'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/student/upload-documents', methods=['POST'])
@login_required(['STUDENT'])
def upload_student_documents():
    """Upload documents for scholarship application"""
    try:
        user_id = session.get('user_id')
        
        # Check if files were uploaded
        if 'files' not in request.files:
            return jsonify({'success': False, 'message': 'No files uploaded'}), 400
        
        files = request.files.getlist('files')
        
        if not files or len(files) == 0:
            return jsonify({'success': False, 'message': 'No files selected'}), 400
        
        # Validate file count (max 5 files)
        if len(files) > 5:
            return jsonify({'success': False, 'message': 'Maximum 5 files allowed'}), 400
        
        uploaded_files = []
        allowed_extensions = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'}
        
        # Create user-specific upload directory
        upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'student_documents', str(user_id))
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        for file in files:
            if file.filename == '':
                continue
            
            # Validate file extension
            file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
            if file_ext not in allowed_extensions:
                return jsonify({
                    'success': False, 
                    'message': f'Invalid file type: {file.filename}. Allowed: PDF, DOC, DOCX, JPG, PNG'
                }), 400
            
            # Validate file size (5MB max)
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            
            if file_size > 5 * 1024 * 1024:
                return jsonify({
                    'success': False, 
                    'message': f'File too large: {file.filename}. Maximum 5MB per file'
                }), 400
            
            # Generate secure filename
            original_name = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{timestamp}_{secrets.token_hex(4)}_{original_name}"
            filepath = os.path.join(upload_dir, unique_filename)
            
            # Save file
            file.save(filepath)
            
            # Store relative path for database
            relative_path = os.path.join('uploads', 'student_documents', str(user_id), unique_filename)
            
            uploaded_files.append({
                'original_name': file.filename,
                'saved_name': unique_filename,
                'file_path': relative_path,
                'file_size': file_size,
                'file_type': file_ext
            })
        
        print(f"[DEBUG] Uploaded {len(uploaded_files)} files for user {user_id}")
        
        return jsonify({
            'success': True,
            'message': f'{len(uploaded_files)} file(s) uploaded successfully',
            'files': uploaded_files
        })
        
    except Exception as e:
        print(f"Error uploading documents: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'Failed to upload documents'}), 500

@app.route('/api/student/apply', methods=['POST'])
@login_required(['STUDENT'])
def submit_scholarship_application():
    """Submit a scholarship application"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        cursor = connection.cursor(dictionary=True)
        
        # Get student ID
        cursor.execute("SELECT id FROM students WHERE user_id = %s", (user_id,))
        student = cursor.fetchone()
        
        if not student:
            return jsonify({'success': False, 'message': 'Student profile not found'}), 404
        
        student_id = student['id']
        scholarship_id = data.get('scholarship_id')
        
        if not scholarship_id:
            return jsonify({'success': False, 'message': 'Scholarship ID is required'}), 400
        
        # Check if scholarship exists and is active
        cursor.execute("""
            SELECT id, is_active, application_deadline 
            FROM scholarships 
            WHERE id = %s
        """, (scholarship_id,))
        scholarship = cursor.fetchone()
        
        if not scholarship:
            return jsonify({'success': False, 'message': 'Scholarship not found'}), 404
        
        if not scholarship['is_active']:
            return jsonify({'success': False, 'message': 'Scholarship is not active'}), 400
        
        if scholarship['application_deadline'] < datetime.now():
            return jsonify({'success': False, 'message': 'Application deadline has passed'}), 400
        
        # Check if student has already applied
        cursor.execute("""
            SELECT id FROM applications 
            WHERE student_id = %s AND scholarship_id = %s
        """, (student_id, scholarship_id))
        
        if cursor.fetchone():
            return jsonify({'success': False, 'message': 'You have already applied for this scholarship'}), 400
        
        # Get uploaded files data (if any)
        uploaded_files = data.get('uploaded_files', [])
        
        # Insert application
        insert_query = """
            INSERT INTO applications 
            (student_id, scholarship_id, status, cover_letter, additional_info, submitted_at, created_at)
            VALUES (%s, %s, 'PENDING', %s, %s, NOW(), NOW())
        """
        
        values = (
            student_id,
            scholarship_id,
            data.get('essay', ''),
            data.get('documents_text', '')  # Optional text description of documents
        )
        
        cursor.execute(insert_query, values)
        connection.commit()
        
        application_id = cursor.lastrowid
        
        # Insert uploaded documents into application_documents table
        if uploaded_files and len(uploaded_files) > 0:
            doc_insert_query = """
                INSERT INTO application_documents 
                (application_id, document_type, document_name, file_path, file_size, mime_type, uploaded_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """
            
            for file_data in uploaded_files:
                doc_values = (
                    application_id,
                    file_data.get('file_type', 'document'),
                    file_data.get('original_name', 'document'),
                    file_data.get('file_path', ''),
                    file_data.get('file_size', 0),
                    file_data.get('file_type', 'application/octet-stream')
                )
                cursor.execute(doc_insert_query, doc_values)
            
            connection.commit()
            print(f"[DEBUG] Inserted {len(uploaded_files)} documents for application {application_id}")
        
        print(f"[DEBUG] Application submitted successfully: ID {application_id}")
        
        return jsonify({
            'success': True,
            'message': 'Application submitted successfully',
            'application_id': application_id
        })
        
    except Exception as e:
        print(f"Error submitting application: {e}")
        import traceback
        traceback.print_exc()
        if connection:
            connection.rollback()
        return jsonify({'success': False, 'message': 'Failed to submit application'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# The `/api/create-test-users` endpoint was removed.
# Test users are already present in the database, so this development-only
# route has been deleted to avoid duplicate insertions or accidental exposure.

# ==================== PROVIDER API ROUTES ====================

@app.route('/api/provider/dashboard-stats')
@login_required(['PROVIDER'])
def provider_dashboard_stats():
    """Get provider dashboard statistics"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        user_id = session.get('user_id')
        cursor = connection.cursor(dictionary=True)
        
        # Get provider ID
        cursor.execute("SELECT id FROM providers WHERE user_id = %s", (user_id,))
        provider = cursor.fetchone()
        
        if not provider:
            return jsonify({'success': False, 'message': 'Provider profile not found'}), 404
        
        provider_id = provider['id']
        
        # Get comprehensive statistics
        stats_query = """
            SELECT 
                (SELECT COUNT(*) FROM scholarships WHERE provider_id = %s) as total_scholarships,
                (SELECT COUNT(*) FROM scholarships WHERE provider_id = %s AND is_active = 1) as active_scholarships,
                (SELECT COUNT(*) FROM applications a 
                 JOIN scholarships s ON a.scholarship_id = s.id 
                 WHERE s.provider_id = %s) as total_applications,
                (SELECT COUNT(*) FROM applications a 
                 JOIN scholarships s ON a.scholarship_id = s.id 
                 WHERE s.provider_id = %s AND a.status = 'PENDING') as pending_applications,
                (SELECT COUNT(*) FROM applications a 
                 JOIN scholarships s ON a.scholarship_id = s.id 
                 WHERE s.provider_id = %s AND a.status = 'APPROVED') as approved_applications,
                (SELECT COUNT(*) FROM applications a 
                 JOIN scholarships s ON a.scholarship_id = s.id 
                 WHERE s.provider_id = %s AND a.status = 'REJECTED') as rejected_applications,
                (SELECT COUNT(*) FROM applications a 
                 JOIN scholarships s ON a.scholarship_id = s.id 
                 WHERE s.provider_id = %s AND a.status = 'UNDER_REVIEW') as review_applications,
                (SELECT COUNT(*) FROM applications a 
                 JOIN scholarships s ON a.scholarship_id = s.id 
                 WHERE s.provider_id = %s 
                 AND a.created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)) as applications_this_month,
                (SELECT COUNT(*) FROM scholarships 
                 WHERE provider_id = %s 
                 AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)) as scholarships_this_month,
                (SELECT SUM(amount) FROM scholarships WHERE provider_id = %s AND is_active = 1) as total_funding
        """
        
        cursor.execute(stats_query, (provider_id,) * 10)
        stats = cursor.fetchone()
        
        # Calculate growth
        stats['applications_growth'] = 15.3  # Placeholder for now
        stats['scholarships_growth'] = 8.7
        
        # Ensure no None values
        for key in stats:
            if stats[key] is None:
                stats[key] = 0
        
        return jsonify({'success': True, 'data': stats})
        
    except Exception as e:
        print(f"Error fetching provider stats: {e}")
        return jsonify({'success': False, 'message': 'Failed to fetch statistics'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/provider/applications-chart')
@login_required(['PROVIDER'])
def provider_applications_chart():
    """Get applications chart data for provider dashboard"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        user_id = session.get('user_id')
        days = request.args.get('days', 30, type=int)
        
        # Limit days to reasonable range
        if days not in [30, 90, 365]:
            days = 30
        
        cursor = connection.cursor(dictionary=True)
        
        # Get provider ID
        cursor.execute("SELECT id FROM providers WHERE user_id = %s", (user_id,))
        provider = cursor.fetchone()
        
        if not provider:
            return jsonify({'success': False, 'message': 'Provider profile not found'}), 404
        
        provider_id = provider['id']
        
        # Determine grouping interval based on days
        if days <= 30:
            # Daily grouping for last 30 days
            group_format = '%Y-%m-%d'
            date_label_format = '%b %d'  # e.g., "Jan 15"
            interval_days = 1
        elif days <= 90:
            # Weekly grouping for last 90 days
            group_format = '%Y-%u'  # Year and week number
            date_label_format = '%b %d'
            interval_days = 7
        else:
            # Monthly grouping for last 365 days
            group_format = '%Y-%m'
            date_label_format = '%b %Y'  # e.g., "Jan 2025"
            interval_days = 30
        
        # Query to get applications grouped by date and status
        chart_query = """
            SELECT 
                DATE(a.created_at) as application_date,
                a.status,
                COUNT(*) as count
            FROM applications a
            JOIN scholarships s ON a.scholarship_id = s.id
            WHERE s.provider_id = %s
            AND a.created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
            GROUP BY DATE(a.created_at), a.status
            ORDER BY application_date ASC
        """
        
        cursor.execute(chart_query, (provider_id, days))
        results = cursor.fetchall()
        
        # Process data into chart format
        data_dict = {}
        for row in results:
            date_str = row['application_date'].strftime(date_label_format)
            status = row['status']
            count = row['count']
            
            if date_str not in data_dict:
                data_dict[date_str] = {'pending': 0, 'approved': 0, 'rejected': 0}
            
            if status == 'PENDING':
                data_dict[date_str]['pending'] = count
            elif status == 'APPROVED':
                data_dict[date_str]['approved'] = count
            elif status == 'REJECTED':
                data_dict[date_str]['rejected'] = count
        
        # Generate complete date range (fill in missing dates with zeros)
        labels = []
        pending = []
        approved = []
        rejected = []
        
        # Calculate number of data points
        if days <= 30:
            num_points = days
        elif days <= 90:
            num_points = 13  # ~13 weeks in 90 days
        else:
            num_points = 12  # 12 months
        
        current_date = datetime.now()
        for i in range(num_points - 1, -1, -1):
            date = current_date - timedelta(days=i * interval_days)
            
            if days <= 30:
                label = date.strftime('%b %d')
            elif days <= 90:
                # Use start of week
                label = date.strftime('%b %d')
            else:
                label = date.strftime('%b %Y')
            
            labels.append(label)
            
            # Get data for this date or default to 0
            if label in data_dict:
                pending.append(data_dict[label]['pending'])
                approved.append(data_dict[label]['approved'])
                rejected.append(data_dict[label]['rejected'])
            else:
                pending.append(0)
                approved.append(0)
                rejected.append(0)
        
        chart_data = {
            'labels': labels,
            'pending': pending,
            'approved': approved,
            'rejected': rejected
        }
        
        return jsonify({'success': True, 'data': chart_data})
        
    except Exception as e:
        print(f"Error fetching chart data: {e}")
        return jsonify({'success': False, 'message': 'Failed to fetch chart data'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/student/dashboard-stats')
@login_required(['STUDENT'])
def student_dashboard_stats():
    """Get student dashboard statistics"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        user_id = session.get('user_id')
        cursor = connection.cursor(dictionary=True)
        
        # Get student ID
        cursor.execute("SELECT id FROM students WHERE user_id = %s", (user_id,))
        student = cursor.fetchone()
        
        if not student:
            return jsonify({'success': False, 'message': 'Student profile not found'}), 404
        
        student_id = student['id']
        
        # Get comprehensive statistics
        stats_query = """
            SELECT 
                (SELECT COUNT(*) FROM applications WHERE student_id = %s) as total_applications,
                (SELECT COUNT(*) FROM applications WHERE student_id = %s AND status = 'PENDING') as pending_applications,
                (SELECT COUNT(*) FROM applications WHERE student_id = %s AND status = 'APPROVED') as approved_applications,
                (SELECT COUNT(*) FROM applications WHERE student_id = %s AND status = 'REJECTED') as rejected_applications,
                (SELECT COALESCE(SUM(s.amount), 0) FROM applications a 
                 JOIN scholarships s ON a.scholarship_id = s.id 
                 WHERE a.student_id = %s AND a.status = 'APPROVED') as total_awarded,
                (SELECT COUNT(*) FROM applications 
                 WHERE student_id = %s 
                 AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)) as applications_this_month
        """
        
        cursor.execute(stats_query, (student_id,) * 6)
        stats = cursor.fetchone()
        
        print(f"=== DASHBOARD STATS DEBUG ===")
        print(f"Student ID: {student_id}")
        print(f"Raw stats from query: {stats}")
        
        # Ensure no None values
        for key in stats:
            if stats[key] is None:
                stats[key] = 0
        
        print(f"Stats after cleanup: {stats}")
        
        return jsonify({'success': True, 'data': stats})
        
    except Exception as e:
        print(f"Error fetching student stats: {e}")
        return jsonify({'success': False, 'message': 'Failed to fetch statistics'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/student/profile')
@login_required(['STUDENT'])
def student_profile():
    """Get student profile information"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        user_id = session.get('user_id')
        cursor = connection.cursor(dictionary=True)
        
        # Get student profile with user details
        query = """
            SELECT s.*, u.email, u.first_name, u.last_name, u.phone_number, u.is_verified
            FROM students s
            JOIN users u ON s.user_id = u.id
            WHERE s.user_id = %s
        """
        
        cursor.execute(query, (user_id,))
        student = cursor.fetchone()
        
        if not student:
            return jsonify({'success': False, 'message': 'Student profile not found'}), 404
        
        # Convert datetime objects to strings for JSON serialization
        for key, value in student.items():
            if hasattr(value, 'strftime'):
                student[key] = value.strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({'success': True, 'profile': student})
        
    except Exception as e:
        print(f"Error fetching student profile: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'Failed to fetch profile'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/student/profile/update', methods=['POST'])
@login_required(['STUDENT'])
def update_student_profile():
    """Update student profile information"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        user_id = session.get('user_id')
        data = request.get_json()
        
        cursor = connection.cursor(dictionary=True)
        
        # Get student ID
        cursor.execute("SELECT id FROM students WHERE user_id = %s", (user_id,))
        student = cursor.fetchone()
        
        if not student:
            return jsonify({'success': False, 'message': 'Student profile not found'}), 404
        
        student_id = student['id']
        
        # Update user table (personal info)
        user_updates = []
        user_values = []
        
        if 'first_name' in data:
            user_updates.append("first_name = %s")
            user_values.append(data['first_name'])
        if 'last_name' in data:
            user_updates.append("last_name = %s")
            user_values.append(data['last_name'])
        if 'phone_number' in data:
            user_updates.append("phone_number = %s")
            user_values.append(data['phone_number'])
        
        if user_updates:
            user_values.append(user_id)
            user_query = f"UPDATE users SET {', '.join(user_updates)} WHERE id = %s"
            cursor.execute(user_query, tuple(user_values))
        
        # Update students table
        student_updates = []
        student_values = []
        
        if 'date_of_birth' in data:
            student_updates.append("date_of_birth = %s")
            student_values.append(data['date_of_birth'])
        if 'gender' in data:
            student_updates.append("gender = %s")
            student_values.append(data['gender'])
        if 'address' in data:
            student_updates.append("address = %s")
            student_values.append(data['address'])
        if 'city' in data:
            student_updates.append("city = %s")
            student_values.append(data['city'])
        if 'student_number' in data:
            student_updates.append("student_number = %s")
            student_values.append(data['student_number'])
        if 'school_name' in data:
            student_updates.append("school_name = %s")
            student_values.append(data['school_name'])
        if 'course' in data:
            student_updates.append("course = %s")
            student_values.append(data['course'])
        if 'year_level' in data:
            student_updates.append("year_level = %s")
            student_values.append(data['year_level'])
        if 'gpa' in data:
            student_updates.append("gpa = %s")
            student_values.append(data['gpa'])
        if 'expected_graduation_date' in data:
            student_updates.append("expected_graduation_date = %s")
            student_values.append(data['expected_graduation_date'])
        if 'family_income' in data:
            student_updates.append("family_income = %s")
            student_values.append(data['family_income'])
        if 'guardian_name' in data:
            student_updates.append("guardian_name = %s")
            student_values.append(data['guardian_name'])
        if 'bio' in data:
            student_updates.append("bio = %s")
            student_values.append(data['bio'])
        
        if student_updates:
            student_values.append(student_id)
            student_query = f"UPDATE students SET {', '.join(student_updates)} WHERE id = %s"
            cursor.execute(student_query, tuple(student_values))
        
        connection.commit()
        
        return jsonify({'success': True, 'message': 'Profile updated successfully'})
        
    except Exception as e:
        if connection:
            connection.rollback()
        print(f"Error updating student profile: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'Failed to update profile'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/student/profile/upload-picture', methods=['POST'])
@login_required(['STUDENT'])
def upload_profile_picture():
    """Upload student profile picture"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        user_id = session.get('user_id')
        cursor = connection.cursor(dictionary=True)
        
        # Get student ID
        cursor.execute("SELECT id, profile_picture FROM students WHERE user_id = %s", (user_id,))
        student = cursor.fetchone()
        
        if not student:
            return jsonify({'success': False, 'message': 'Student profile not found'}), 404
        
        student_id = student['id']
        old_picture = student['profile_picture']
        
        # Check if file was uploaded
        if 'profile_picture' not in request.files:
            return jsonify({'success': False, 'message': 'No file uploaded'}), 400
        
        file = request.files['profile_picture']
        
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        # Validate file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        
        if file_ext not in allowed_extensions:
            return jsonify({'success': False, 'message': 'Invalid file type. Allowed: PNG, JPG, JPEG, GIF, WEBP'}), 400
        
        # Validate file size (max 2MB)
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > 2 * 1024 * 1024:  # 2MB
            return jsonify({'success': False, 'message': 'File size must be less than 2MB'}), 400
        
        # Create directory for profile pictures
        profile_pics_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'profile_pictures')
        os.makedirs(profile_pics_dir, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        random_token = secrets.token_hex(8)
        safe_filename = secure_filename(file.filename)
        unique_filename = f"{timestamp}_{random_token}_{safe_filename}"
        
        # Save file
        file_path = os.path.join(profile_pics_dir, unique_filename)
        file.save(file_path)
        
        # Store relative path in database (URL-compatible with forward slashes)
        relative_path = f'uploads/profile_pictures/{unique_filename}'
        
        # Update database
        cursor.execute(
            "UPDATE students SET profile_picture = %s WHERE id = %s",
            (relative_path, student_id)
        )
        connection.commit()
        
        # Delete old profile picture if exists
        if old_picture:
            try:
                old_file_path = os.path.join(os.path.dirname(app.config['UPLOAD_FOLDER']), old_picture.replace('/', os.sep))
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
            except Exception as e:
                print(f"Error deleting old profile picture: {e}")
        
        return jsonify({
            'success': True,
            'message': 'Profile picture uploaded successfully',
            'profile_picture': relative_path
        })
        
    except Exception as e:
        if connection:
            connection.rollback()
        print(f"Error uploading profile picture: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'Failed to upload profile picture'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/student/profile/remove-picture', methods=['DELETE'])
@login_required(['STUDENT'])
def remove_profile_picture():
    """Remove student profile picture"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        user_id = session.get('user_id')
        cursor = connection.cursor(dictionary=True)
        
        # Get student ID and current profile picture
        cursor.execute("SELECT id, profile_picture FROM students WHERE user_id = %s", (user_id,))
        student = cursor.fetchone()
        
        if not student:
            return jsonify({'success': False, 'message': 'Student profile not found'}), 404
        
        student_id = student['id']
        profile_picture = student['profile_picture']
        
        if not profile_picture:
            return jsonify({'success': False, 'message': 'No profile picture to remove'}), 400
        
        # Update database - set profile_picture to NULL
        cursor.execute(
            "UPDATE students SET profile_picture = NULL WHERE id = %s",
            (student_id,)
        )
        connection.commit()
        
        # Delete file from filesystem
        try:
            file_path = os.path.join(os.path.dirname(app.config['UPLOAD_FOLDER']), profile_picture.replace('/', os.sep))
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Deleted profile picture: {file_path}")
            else:
                print(f"Profile picture file not found: {file_path}")
        except Exception as e:
            print(f"Error deleting profile picture file: {e}")
            # Don't fail the request if file deletion fails
        
        return jsonify({
            'success': True,
            'message': 'Profile picture removed successfully'
        })
        
    except Exception as e:
        if connection:
            connection.rollback()
        print(f"Error removing profile picture: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'Failed to remove profile picture'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/student/profile/documents')
@login_required(['STUDENT'])
def get_student_profile_documents():
    """Get student's profile documents"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        user_id = session.get('user_id')
        cursor = connection.cursor(dictionary=True)
        
        # Get student ID
        cursor.execute("SELECT id FROM students WHERE user_id = %s", (user_id,))
        student = cursor.fetchone()
        
        if not student:
            return jsonify({'success': False, 'message': 'Student profile not found'}), 404
        
        student_id = student['id']
        
        # Get documents
        query = """
            SELECT id, document_type, document_name, file_path, file_size, 
                   mime_type, is_verified, uploaded_at
            FROM student_documents
            WHERE student_id = %s
            ORDER BY uploaded_at DESC
        """
        
        cursor.execute(query, (student_id,))
        documents = cursor.fetchall()
        
        # Convert datetime objects to strings
        for doc in documents:
            for key, value in doc.items():
                if hasattr(value, 'strftime'):
                    doc[key] = value.strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({'success': True, 'documents': documents})
        
    except Exception as e:
        print(f"Error fetching documents: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'Failed to fetch documents'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/student/profile/documents/upload', methods=['POST'])
@login_required(['STUDENT'])
def upload_profile_document():
    """Upload a profile document"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        user_id = session.get('user_id')
        cursor = connection.cursor(dictionary=True)
        
        # Get student ID
        cursor.execute("SELECT id FROM students WHERE user_id = %s", (user_id,))
        student = cursor.fetchone()
        
        if not student:
            return jsonify({'success': False, 'message': 'Student profile not found'}), 404
        
        student_id = student['id']
        
        # Check if files were uploaded
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file provided'}), 400
        
        file = request.files['file']
        document_type = request.form.get('document_type', 'Other')
        
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        # Validate file type
        allowed_extensions = {'pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'}
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        
        if file_ext not in allowed_extensions:
            return jsonify({'success': False, 'message': 'Invalid file type'}), 400
        
        # Validate file size (5MB max)
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if file_size > 5 * 1024 * 1024:  # 5MB
            return jsonify({'success': False, 'message': 'File too large (max 5MB)'}), 400
        
        # Create upload directory
        upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'profile_documents', str(student_id))
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_token = secrets.token_hex(8)
        safe_filename = secure_filename(file.filename)
        unique_filename = f"{timestamp}_{unique_token}_{safe_filename}"
        
        # Save file
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)
        
        # Get MIME type
        mime_type = file.content_type
        
        # Save to database (use forward slashes for URL compatibility)
        relative_path = f'uploads/profile_documents/{student_id}/{unique_filename}'
        
        query = """
            INSERT INTO student_documents 
            (student_id, document_type, document_name, file_path, file_size, mime_type, uploaded_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
        """
        
        cursor.execute(query, (
            student_id,
            document_type,
            safe_filename,
            relative_path,
            file_size,
            mime_type
        ))
        
        connection.commit()
        document_id = cursor.lastrowid
        
        return jsonify({
            'success': True,
            'message': 'Document uploaded successfully',
            'document': {
                'id': document_id,
                'document_type': document_type,
                'document_name': safe_filename,
                'file_size': file_size
            }
        })
        
    except Exception as e:
        if connection:
            connection.rollback()
        print(f"Error uploading document: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'Failed to upload document'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/student/profile/documents/<int:document_id>', methods=['DELETE'])
@login_required(['STUDENT'])
def delete_profile_document(document_id):
    """Delete a profile document"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        user_id = session.get('user_id')
        cursor = connection.cursor(dictionary=True)
        
        # Get student ID
        cursor.execute("SELECT id FROM students WHERE user_id = %s", (user_id,))
        student = cursor.fetchone()
        
        if not student:
            return jsonify({'success': False, 'message': 'Student profile not found'}), 404
        
        student_id = student['id']
        
        # Get document info
        cursor.execute(
            "SELECT file_path FROM student_documents WHERE id = %s AND student_id = %s",
            (document_id, student_id)
        )
        document = cursor.fetchone()
        
        if not document:
            return jsonify({'success': False, 'message': 'Document not found'}), 404
        
        # Delete file from filesystem
        file_path = document['file_path']
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error deleting file: {e}")
        
        # Delete from database
        cursor.execute("DELETE FROM student_documents WHERE id = %s AND student_id = %s", 
                      (document_id, student_id))
        connection.commit()
        
        return jsonify({'success': True, 'message': 'Document deleted successfully'})
        
    except Exception as e:
        if connection:
            connection.rollback()
        print(f"Error deleting document: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'Failed to delete document'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/student/recent-applications')
@login_required(['STUDENT'])
def student_recent_applications():
    """Get student's recent applications with scholarship details"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        user_id = session.get('user_id')
        cursor = connection.cursor(dictionary=True)
        
        # Get student ID
        cursor.execute("SELECT id FROM students WHERE user_id = %s", (user_id,))
        student = cursor.fetchone()
        
        if not student:
            return jsonify({'success': False, 'message': 'Student profile not found'}), 404
        
        student_id = student['id']
        
        # Get recent applications with scholarship details
        query = """
            SELECT 
                a.id as application_id,
                a.status,
                a.created_at as applied_date,
                s.title as scholarship_title,
                s.amount,
                s.application_deadline,
                p.organization_name as provider_name
            FROM applications a
            JOIN scholarships s ON a.scholarship_id = s.id
            JOIN providers p ON s.provider_id = p.id
            WHERE a.student_id = %s
            ORDER BY a.created_at DESC
            LIMIT 3
        """
        
        cursor.execute(query, (student_id,))
        applications = cursor.fetchall()
        
        print(f"=== RECENT APPLICATIONS DEBUG ===")
        print(f"Student ID: {student_id}")
        print(f"Applications found: {len(applications)}")
        print(f"Applications data: {applications}")
        
        # Convert datetime objects to strings
        for app in applications:
            for key, value in app.items():
                if hasattr(value, 'strftime'):
                    app[key] = value.strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"After conversion: {applications}")
        
        return jsonify({'success': True, 'applications': applications})
        
    except Exception as e:
        print(f"Error fetching recent applications: {e}")
        return jsonify({'success': False, 'message': 'Failed to fetch applications'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/student/new-scholarships')
@login_required(['STUDENT'])
def student_new_scholarships():
    """Get newly uploaded active scholarships"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Get newly uploaded scholarships (last 30 days)
        query = """
            SELECT 
                s.id,
                s.title,
                s.description,
                s.amount,
                s.scholarship_type as category,
                s.application_deadline as deadline,
                s.created_at,
                p.organization_name as provider_name
            FROM scholarships s
            JOIN providers p ON s.provider_id = p.id
            WHERE s.is_active = 1 
            AND s.application_deadline >= NOW()
            AND s.created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            ORDER BY s.created_at DESC
            LIMIT 3
        """
        
        cursor.execute(query)
        scholarships = cursor.fetchall()
        
        # Convert datetime objects to strings
        for scholarship in scholarships:
            for key, value in scholarship.items():
                if hasattr(value, 'strftime'):
                    scholarship[key] = value.strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({'success': True, 'scholarships': scholarships})
        
    except Exception as e:
        print(f"Error fetching new scholarships: {e}")
        return jsonify({'success': False, 'message': 'Failed to fetch scholarships'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/student/saved-scholarships', methods=['GET'])
@login_required(['STUDENT'])
def get_saved_scholarships():
    """Get all saved/bookmarked scholarships for current student"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        user_id = session.get('user_id')
        cursor = connection.cursor(dictionary=True)
        
        # Get student ID
        cursor.execute("SELECT id FROM students WHERE user_id = %s", (user_id,))
        student = cursor.fetchone()
        
        if not student:
            return jsonify({'success': False, 'message': 'Student profile not found'}), 404
        
        student_id = student['id']
        
        # Get saved scholarships with details
        query = """
        SELECT 
            ss.id as saved_id,
            ss.created_at as saved_date,
            s.id as scholarship_id,
            s.title,
            s.description,
            s.amount,
            s.scholarship_type,
            s.application_deadline,
            s.is_active,
            s.available_slots,
            p.organization_name as provider_name,
            (SELECT COUNT(*) FROM applications WHERE scholarship_id = s.id AND student_id = %s) as has_applied
        FROM saved_scholarships ss
        JOIN scholarships s ON ss.scholarship_id = s.id
        JOIN providers p ON s.provider_id = p.id
        WHERE ss.student_id = %s AND s.is_active = 1
        ORDER BY ss.created_at DESC
        """
        
        cursor.execute(query, (student_id, student_id))
        saved_scholarships = cursor.fetchall()
        
        # Serialize datetime objects
        for scholarship in saved_scholarships:
            for key, value in scholarship.items():
                if hasattr(value, 'strftime'):
                    scholarship[key] = value.strftime('%Y-%m-%d %H:%M:%S')
        
        # Get statistics
        total_saved = len(saved_scholarships)
        total_value = sum(s['amount'] for s in saved_scholarships)
        
        # Count scholarships expiring soon (within 30 days)
        from datetime import datetime, timedelta
        thirty_days_later = datetime.now() + timedelta(days=30)
        expiring_soon = sum(1 for s in saved_scholarships 
                          if datetime.strptime(s['application_deadline'], '%Y-%m-%d %H:%M:%S') <= thirty_days_later)
        
        stats = {
            'total_saved': total_saved,
            'total_value': total_value,
            'expiring_soon': expiring_soon
        }
        
        print(f"[DEBUG] Found {total_saved} saved scholarships for student {student_id}")
        
        return jsonify({
            'success': True,
            'scholarships': saved_scholarships,
            'stats': stats
        })
        
    except Exception as e:
        print(f"Error fetching saved scholarships: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'Failed to fetch saved scholarships'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/student/save-scholarship/<int:scholarship_id>', methods=['POST'])
@login_required(['STUDENT'])
def save_scholarship(scholarship_id):
    """Save/bookmark a scholarship"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        user_id = session.get('user_id')
        cursor = connection.cursor(dictionary=True)
        
        # Get student ID
        cursor.execute("SELECT id FROM students WHERE user_id = %s", (user_id,))
        student = cursor.fetchone()
        
        if not student:
            return jsonify({'success': False, 'message': 'Student profile not found'}), 404
        
        student_id = student['id']
        
        # Check if scholarship exists
        cursor.execute("SELECT id FROM scholarships WHERE id = %s", (scholarship_id,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': 'Scholarship not found'}), 404
        
        # Check if already saved
        cursor.execute("""
            SELECT id FROM saved_scholarships 
            WHERE student_id = %s AND scholarship_id = %s
        """, (student_id, scholarship_id))
        
        if cursor.fetchone():
            return jsonify({'success': False, 'message': 'Scholarship already saved'}), 400
        
        # Save the scholarship
        cursor.execute("""
            INSERT INTO saved_scholarships (student_id, scholarship_id, created_at)
            VALUES (%s, %s, NOW())
        """, (student_id, scholarship_id))
        
        connection.commit()
        
        print(f"[DEBUG] Student {student_id} saved scholarship {scholarship_id}")
        
        return jsonify({
            'success': True,
            'message': 'Scholarship saved successfully'
        })
        
    except Exception as e:
        print(f"Error saving scholarship: {e}")
        import traceback
        traceback.print_exc()
        if connection:
            connection.rollback()
        return jsonify({'success': False, 'message': 'Failed to save scholarship'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/student/unsave-scholarship/<int:scholarship_id>', methods=['DELETE'])
@login_required(['STUDENT'])
def unsave_scholarship(scholarship_id):
    """Remove a saved/bookmarked scholarship"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        user_id = session.get('user_id')
        cursor = connection.cursor(dictionary=True)
        
        # Get student ID
        cursor.execute("SELECT id FROM students WHERE user_id = %s", (user_id,))
        student = cursor.fetchone()
        
        if not student:
            return jsonify({'success': False, 'message': 'Student profile not found'}), 404
        
        student_id = student['id']
        
        # Remove the saved scholarship
        cursor.execute("""
            DELETE FROM saved_scholarships 
            WHERE student_id = %s AND scholarship_id = %s
        """, (student_id, scholarship_id))
        
        connection.commit()
        
        if cursor.rowcount == 0:
            return jsonify({'success': False, 'message': 'Scholarship was not saved'}), 404
        
        print(f"[DEBUG] Student {student_id} unsaved scholarship {scholarship_id}")
        
        return jsonify({
            'success': True,
            'message': 'Scholarship removed from saved list'
        })
        
    except Exception as e:
        print(f"Error unsaving scholarship: {e}")
        import traceback
        traceback.print_exc()
        if connection:
            connection.rollback()
        return jsonify({'success': False, 'message': 'Failed to remove scholarship'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/provider/scholarships')
@login_required(['PROVIDER'])
def provider_scholarships():
    """Get all scholarships for current provider"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        user_id = session.get('user_id')
        cursor = connection.cursor(dictionary=True)
        
        # Get provider ID
        cursor.execute("SELECT id, organization_name FROM providers WHERE user_id = %s", (user_id,))
        provider = cursor.fetchone()
        
        print(f"[DEBUG] Loading scholarships for user_id: {user_id}, provider: {provider}")
        
        if not provider:
            return jsonify({'success': False, 'message': 'Provider profile not found'}), 404
        
        # Get all scholarships with application counts
        query = """
            SELECT 
                s.*,
                p.organization_name,
                (SELECT COUNT(*) FROM applications WHERE scholarship_id = s.id) as application_count,
                (SELECT COUNT(*) FROM applications WHERE scholarship_id = s.id AND status = 'PENDING') as pending_count,
                (SELECT COUNT(*) FROM applications WHERE scholarship_id = s.id AND status = 'APPROVED') as approved_count
            FROM scholarships s
            JOIN providers p ON s.provider_id = p.id
            WHERE s.provider_id = %s
            ORDER BY s.created_at DESC
        """
        
        cursor.execute(query, (provider['id'],))
        scholarships = cursor.fetchall()
        
        print(f"[DEBUG] Found {len(scholarships)} scholarships for provider_id: {provider['id']}")
        
        # Map database fields to frontend expected fields for each scholarship
        for scholarship in scholarships:
            # Convert datetime objects to strings for JSON serialization
            if scholarship.get('application_deadline'):
                if hasattr(scholarship['application_deadline'], 'strftime'):
                    scholarship['deadline'] = scholarship['application_deadline'].strftime('%Y-%m-%d')
                    scholarship['application_deadline'] = scholarship['application_deadline'].strftime('%Y-%m-%d')
                else:
                    scholarship['deadline'] = str(scholarship['application_deadline'])
            
            if scholarship.get('created_at'):
                scholarship['created_at'] = scholarship['created_at'].strftime('%Y-%m-%d %H:%M:%S') if hasattr(scholarship['created_at'], 'strftime') else str(scholarship['created_at'])
            
            if scholarship.get('updated_at'):
                scholarship['updated_at'] = scholarship['updated_at'].strftime('%Y-%m-%d %H:%M:%S') if hasattr(scholarship['updated_at'], 'strftime') else str(scholarship['updated_at'])
            
            # Map scholarship_type to category for frontend
            type_to_category = {
                'FULL_SCHOLARSHIP': 'Engineering',
                'PARTIAL_SCHOLARSHIP': 'General',
                'MONTHLY_ALLOWANCE': 'General',
                'ONE_TIME_GRANT': 'General'
            }
            scholarship['category'] = type_to_category.get(scholarship.get('scholarship_type'), 'General')
        
        return jsonify({'success': True, 'scholarships': scholarships})
        
    except Exception as e:
        print(f"Error fetching scholarships: {e}")
        return jsonify({'success': False, 'message': 'Failed to fetch scholarships'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/provider/scholarship/<int:scholarship_id>')
@login_required(['PROVIDER'])
def provider_scholarship_detail(scholarship_id):
    """Get scholarship details"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        user_id = session.get('user_id')
        cursor = connection.cursor(dictionary=True)
        
        # Verify ownership
        query = """
            SELECT s.*, p.organization_name
            FROM scholarships s
            JOIN providers p ON s.provider_id = p.id
            WHERE s.id = %s AND p.user_id = %s
        """
        
        cursor.execute(query, (scholarship_id, user_id))
        scholarship = cursor.fetchone()
        
        if not scholarship:
            return jsonify({'success': False, 'message': 'Scholarship not found'}), 404
        
        # Convert datetime objects to strings for JSON serialization
        if scholarship.get('application_deadline'):
            if hasattr(scholarship['application_deadline'], 'strftime'):
                scholarship['deadline'] = scholarship['application_deadline'].strftime('%Y-%m-%d')
                scholarship['application_deadline'] = scholarship['application_deadline'].strftime('%Y-%m-%d')
            else:
                scholarship['deadline'] = str(scholarship['application_deadline'])
        
        if scholarship.get('created_at'):
            scholarship['created_at'] = scholarship['created_at'].strftime('%Y-%m-%d %H:%M:%S') if hasattr(scholarship['created_at'], 'strftime') else str(scholarship['created_at'])
        
        if scholarship.get('updated_at'):
            scholarship['updated_at'] = scholarship['updated_at'].strftime('%Y-%m-%d %H:%M:%S') if hasattr(scholarship['updated_at'], 'strftime') else str(scholarship['updated_at'])
        
        # Map scholarship_type to category for frontend
        type_to_category = {
            'FULL_SCHOLARSHIP': 'Engineering',
            'PARTIAL_SCHOLARSHIP': 'General',
            'MONTHLY_ALLOWANCE': 'General',
            'ONE_TIME_GRANT': 'General'
        }
        scholarship['category'] = type_to_category.get(scholarship.get('scholarship_type'), 'General')
        
        return jsonify({'success': True, 'scholarship': scholarship})
        
    except Exception as e:
        print(f"Error fetching scholarship: {e}")
        return jsonify({'success': False, 'message': 'Failed to fetch scholarship'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/provider/scholarship', methods=['POST'])
@login_required(['PROVIDER'])
def create_scholarship():
    """Create a new scholarship"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        cursor = connection.cursor(dictionary=True)
        
        print(f"[DEBUG] Creating scholarship for user_id: {user_id}")
        print(f"[DEBUG] Scholarship data: {data}")
        
        # Get provider ID
        cursor.execute("SELECT id FROM providers WHERE user_id = %s", (user_id,))
        provider = cursor.fetchone()
        
        print(f"[DEBUG] Provider found: {provider}")
        
        if not provider:
            return jsonify({'success': False, 'message': 'Provider profile not found'}), 404
        
        # Validate required fields
        required_fields = ['title', 'description', 'amount', 'deadline', 'eligibility_criteria']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'{field} is required'}), 400
        
        # Map scholarship_type from category or use default
        scholarship_type_map = {
            'Engineering': 'FULL_SCHOLARSHIP',
            'Medicine': 'FULL_SCHOLARSHIP',
            'Business': 'PARTIAL_SCHOLARSHIP',
            'Science': 'FULL_SCHOLARSHIP',
            'Technology': 'PARTIAL_SCHOLARSHIP',
            'General': 'PARTIAL_SCHOLARSHIP'
        }
        scholarship_type = scholarship_type_map.get(data.get('category', 'General'), 'PARTIAL_SCHOLARSHIP')
        
        # Insert scholarship
        insert_query = """
            INSERT INTO scholarships 
            (provider_id, title, description, scholarship_type, amount, available_slots,
             eligibility_criteria, required_documents, application_deadline, is_active, 
             created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        """
        
        values = (
            provider['id'],
            data['title'],
            data['description'],
            scholarship_type,
            data['amount'],
            data.get('available_slots'),
            data['eligibility_criteria'],
            data.get('required_documents', ''),
            data['deadline'],  # This maps to application_deadline in DB
            data.get('is_active', 1)
        )
        
        cursor.execute(insert_query, values)
        connection.commit()
        
        scholarship_id = cursor.lastrowid
        
        print(f"[DEBUG] Scholarship created successfully with ID: {scholarship_id}")
        
        return jsonify({
            'success': True,
            'message': 'Scholarship created successfully',
            'scholarship_id': scholarship_id
        })
        
    except Exception as e:
        print(f"Error creating scholarship: {e}")
        if connection:
            connection.rollback()
        return jsonify({'success': False, 'message': 'Failed to create scholarship'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/provider/scholarship/<int:scholarship_id>', methods=['PUT'])
@login_required(['PROVIDER'])
def update_scholarship(scholarship_id):
    """Update a scholarship"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        cursor = connection.cursor(dictionary=True)
        
        # Verify ownership
        verify_query = """
            SELECT s.id FROM scholarships s
            JOIN providers p ON s.provider_id = p.id
            WHERE s.id = %s AND p.user_id = %s
        """
        cursor.execute(verify_query, (scholarship_id, user_id))
        
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': 'Scholarship not found or unauthorized'}), 404
        
        # Map scholarship_type from category or use default
        scholarship_type_map = {
            'Engineering': 'FULL_SCHOLARSHIP',
            'Medicine': 'FULL_SCHOLARSHIP',
            'Business': 'PARTIAL_SCHOLARSHIP',
            'Science': 'FULL_SCHOLARSHIP',
            'Technology': 'PARTIAL_SCHOLARSHIP',
            'General': 'PARTIAL_SCHOLARSHIP'
        }
        scholarship_type = scholarship_type_map.get(data.get('category', 'General'), 'PARTIAL_SCHOLARSHIP')
        
        # Update scholarship
        update_query = """
            UPDATE scholarships 
            SET title = %s, description = %s, scholarship_type = %s, amount = %s, 
                available_slots = %s, application_deadline = %s, eligibility_criteria = %s, 
                required_documents = %s, is_active = %s, updated_at = NOW()
            WHERE id = %s
        """
        
        values = (
            data['title'],
            data['description'],
            scholarship_type,
            data['amount'],
            data.get('available_slots'),
            data['deadline'],
            data['eligibility_criteria'],
            data.get('required_documents', ''),
            data.get('is_active', 1),
            scholarship_id
        )
        
        cursor.execute(update_query, values)
        connection.commit()
        
        return jsonify({'success': True, 'message': 'Scholarship updated successfully'})
        
    except Exception as e:
        print(f"Error updating scholarship: {e}")
        if connection:
            connection.rollback()
        return jsonify({'success': False, 'message': 'Failed to update scholarship'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/provider/scholarship/<int:scholarship_id>/toggle', methods=['POST'])
@login_required(['PROVIDER'])
def toggle_provider_scholarship_status(scholarship_id):
    """Toggle scholarship active status"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        user_id = session.get('user_id')
        cursor = connection.cursor(dictionary=True)
        
        # Verify ownership and get current status
        verify_query = """
            SELECT s.id, s.is_active FROM scholarships s
            JOIN providers p ON s.provider_id = p.id
            WHERE s.id = %s AND p.user_id = %s
        """
        cursor.execute(verify_query, (scholarship_id, user_id))
        scholarship = cursor.fetchone()
        
        if not scholarship:
            return jsonify({'success': False, 'message': 'Scholarship not found'}), 404
        
        # Toggle status
        new_status = 0 if scholarship['is_active'] else 1
        cursor.execute("UPDATE scholarships SET is_active = %s WHERE id = %s", (new_status, scholarship_id))
        connection.commit()
        
        return jsonify({
            'success': True,
            'message': f"Scholarship {'activated' if new_status else 'deactivated'} successfully",
            'is_active': bool(new_status)
        })
        
    except Exception as e:
        print(f"Error toggling scholarship: {e}")
        if connection:
            connection.rollback()
        return jsonify({'success': False, 'message': 'Failed to toggle scholarship'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/provider/scholarship/<int:scholarship_id>', methods=['DELETE'])
@login_required(['PROVIDER'])
def delete_scholarship(scholarship_id):
    """Delete a scholarship"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        user_id = session.get('user_id')
        cursor = connection.cursor(dictionary=True)
        
        # Verify ownership
        verify_query = """
            SELECT s.id FROM scholarships s
            JOIN providers p ON s.provider_id = p.id
            WHERE s.id = %s AND p.user_id = %s
        """
        cursor.execute(verify_query, (scholarship_id, user_id))
        
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': 'Scholarship not found or unauthorized'}), 404
        
        # Delete the scholarship (applications will be handled by foreign key constraints or cascade)
        cursor.execute("DELETE FROM scholarships WHERE id = %s", (scholarship_id,))
        connection.commit()
        
        return jsonify({'success': True, 'message': 'Scholarship deleted successfully'})
        
    except Exception as e:
        print(f"Error deleting scholarship: {e}")
        if connection:
            connection.rollback()
        return jsonify({'success': False, 'message': 'Failed to delete scholarship'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/provider/applications')
@login_required(['PROVIDER'])
def provider_applications():
    """Get all applications for provider's scholarships"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    cursor = None
    try:
        user_id = session.get('user_id')
        cursor = connection.cursor(dictionary=True)
        
        # First, check if provider exists
        cursor.execute("SELECT id FROM providers WHERE user_id = %s", (user_id,))
        provider = cursor.fetchone()
        
        if not provider:
            print(f"Provider not found for user_id: {user_id}")
            return jsonify({'success': True, 'applications': [], 'message': 'No provider profile found'})
        
        provider_id = provider['id']
        print(f"Provider ID: {provider_id}, User ID: {user_id}")
        
        # Get all applications with student and scholarship details
        query = """
            SELECT 
                a.*,
                s.title as scholarship_title,
                s.amount as scholarship_amount,
                u.first_name as student_first_name,
                u.last_name as student_last_name,
                u.email as student_email,
                st.school_name,
                st.gpa,
                (SELECT COUNT(*) FROM application_documents ad WHERE ad.application_id = a.id) as documents_count
            FROM applications a
            JOIN scholarships s ON a.scholarship_id = s.id
            JOIN students st ON a.student_id = st.id
            JOIN users u ON st.user_id = u.id
            JOIN providers p ON s.provider_id = p.id
            WHERE p.user_id = %s
            ORDER BY a.created_at DESC
        """
        
        cursor.execute(query, (user_id,))
        applications = cursor.fetchall()
        
        print(f"Found {len(applications)} applications for provider {provider_id}")
        
        # Format dates - handle all datetime fields
        for app in applications:
            # Convert all datetime objects to strings
            for key, value in app.items():
                if hasattr(value, 'strftime'):  # Check if it's a datetime object
                    app[key] = value.strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({'success': True, 'applications': applications})
        
    except Exception as e:
        print(f"Error fetching applications: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Failed to fetch applications: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/provider/application/<int:application_id>')
@login_required(['PROVIDER'])
def provider_application_detail(application_id):
    """Get detailed application information"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        user_id = session.get('user_id')
        cursor = connection.cursor(dictionary=True)
        
        # Get application with full details
        query = """
            SELECT 
                a.*,
                s.title as scholarship_title,
                s.amount as scholarship_amount,
                s.description as scholarship_description,
                st.school_name,
                st.gpa,
                st.course,
                st.year_level,
                st.student_number,
                st.guardian_name,
                st.guardian_phone,
                u.first_name,
                u.last_name,
                u.email as user_email,
                u.phone_number
            FROM applications a
            JOIN scholarships s ON a.scholarship_id = s.id
            JOIN students st ON a.student_id = st.id
            JOIN users u ON st.user_id = u.id
            JOIN providers p ON s.provider_id = p.id
            WHERE a.id = %s AND p.user_id = %s
        """
        
        cursor.execute(query, (application_id, user_id))
        application = cursor.fetchone()
        
        if not application:
            return jsonify({'success': False, 'message': 'Application not found'}), 404
        
        # Convert datetime fields to strings
        for key, value in application.items():
            if hasattr(value, 'strftime'):
                application[key] = value.strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({'success': True, 'application': application})
        
    except Exception as e:
        print(f"Error fetching application: {e}")
        return jsonify({'success': False, 'message': 'Failed to fetch application'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/provider/application/<int:application_id>/status', methods=['POST'])
@login_required(['PROVIDER'])
def update_application_status(application_id):
    """Update application status (approve/reject/review)"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        status = data.get('status')
        notes = data.get('notes', '')
        
        if status not in ['PENDING', 'APPROVED', 'REJECTED', 'UNDER_REVIEW']:
            return jsonify({'success': False, 'message': 'Invalid status'}), 400
        
        cursor = connection.cursor(dictionary=True)
        
        # Verify ownership
        verify_query = """
            SELECT a.id FROM applications a
            JOIN scholarships s ON a.scholarship_id = s.id
            JOIN providers p ON s.provider_id = p.id
            WHERE a.id = %s AND p.user_id = %s
        """
        cursor.execute(verify_query, (application_id, user_id))
        
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': 'Application not found'}), 404
        
        # Update status
        update_query = """
            UPDATE applications 
            SET status = %s, reviewer_notes = %s, reviewed_at = NOW()
            WHERE id = %s
        """
        
        cursor.execute(update_query, (status, notes, application_id))
        connection.commit()
        
        return jsonify({
            'success': True,
            'message': f'Application {status.lower()} successfully'
        })
        
    except Exception as e:
        print(f"Error updating application: {e}")
        if connection:
            connection.rollback()
        return jsonify({'success': False, 'message': 'Failed to update application'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/provider/application/<int:application_id>/documents')
@login_required(['PROVIDER'])
def get_application_documents(application_id):
    """Get documents for a specific application"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    cursor = None
    try:
        user_id = session.get('user_id')
        cursor = connection.cursor(dictionary=True)
        
        # Verify that the provider owns the scholarship for this application
        verify_query = """
            SELECT a.id FROM applications a
            JOIN scholarships s ON a.scholarship_id = s.id
            JOIN providers p ON s.provider_id = p.id
            WHERE a.id = %s AND p.user_id = %s
        """
        cursor.execute(verify_query, (application_id, user_id))
        
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': 'Application not found or access denied'}), 404
        
        # Fetch documents for this application
        documents_query = """
            SELECT 
                id,
                document_type,
                document_name as file_name,
                file_path,
                file_size,
                mime_type as file_type,
                uploaded_at
            FROM application_documents
            WHERE application_id = %s
            ORDER BY uploaded_at DESC
        """
        
        cursor.execute(documents_query, (application_id,))
        documents = cursor.fetchall()
        
        # Convert datetime objects to strings
        for doc in documents:
            if doc.get('uploaded_at'):
                doc['uploaded_at'] = doc['uploaded_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({
            'success': True,
            'documents': documents,
            'count': len(documents)
        })
        
    except Exception as e:
        print(f"Error fetching application documents: {e}")
        return jsonify({'success': False, 'message': 'Failed to fetch documents'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/provider/profile')
@login_required(['PROVIDER'])
def provider_profile():
    """Get provider profile information"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        user_id = session.get('user_id')
        cursor = connection.cursor(dictionary=True)
        
        # Get provider profile with user details
        query = """
            SELECT p.*, u.email, u.first_name, u.last_name, u.phone_number, u.is_verified
            FROM providers p
            JOIN users u ON p.user_id = u.id
            WHERE p.user_id = %s
        """
        
        cursor.execute(query, (user_id,))
        provider = cursor.fetchone()
        
        if not provider:
            return jsonify({'success': False, 'message': 'Provider profile not found'}), 404
        
        # Convert datetime objects to strings for JSON serialization
        for key, value in provider.items():
            if hasattr(value, 'strftime'):
                provider[key] = value.strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({'success': True, 'profile': provider})
        
    except Exception as e:
        print(f"Error fetching provider profile: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'Failed to fetch profile'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/provider/profile', methods=['PUT'])
@login_required(['PROVIDER'])
def update_provider_profile():
    """Update provider profile"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        cursor = connection.cursor()
        
        # Update provider table
        provider_update = """
            UPDATE providers 
            SET organization_name = %s, organization_type = %s, website = %s,
                contact_person = %s, contact_title = %s, address = %s,
                city = %s, state = %s, zip_code = %s, description = %s,
                updated_at = NOW()
            WHERE user_id = %s
        """
        
        provider_values = (
            data.get('organization_name'),
            data.get('organization_type'),
            data.get('website'),
            data.get('contact_person'),
            data.get('contact_title'),
            data.get('address'),
            data.get('city'),
            data.get('state'),
            data.get('zip_code'),
            data.get('description'),
            user_id
        )
        
        cursor.execute(provider_update, provider_values)
        
        # Update user table
        user_update = """
            UPDATE users 
            SET first_name = %s, last_name = %s, phone_number = %s, updated_at = NOW()
            WHERE id = %s
        """
        
        user_values = (
            data.get('first_name'),
            data.get('last_name'),
            data.get('phone_number'),
            user_id
        )
        
        cursor.execute(user_update, user_values)
        connection.commit()
        
        return jsonify({'success': True, 'message': 'Profile updated successfully'})
        
    except Exception as e:
        print(f"Error updating provider profile: {e}")
        if connection:
            connection.rollback()
        return jsonify({'success': False, 'message': 'Failed to update profile'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/provider/analytics')
@login_required(['PROVIDER'])
def provider_analytics():
    """Get detailed analytics for provider"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        user_id = session.get('user_id')
        cursor = connection.cursor(dictionary=True)
        
        # Get provider ID
        cursor.execute("SELECT id FROM providers WHERE user_id = %s", (user_id,))
        provider = cursor.fetchone()
        
        if not provider:
            return jsonify({'success': False, 'message': 'Provider profile not found'}), 404
        
        provider_id = provider['id']
        
        # Get monthly application trends (last 6 months)
        trends_query = """
            SELECT 
                DATE_FORMAT(a.created_at, '%Y-%m') as month,
                COUNT(*) as application_count
            FROM applications a
            JOIN scholarships s ON a.scholarship_id = s.id
            WHERE s.provider_id = %s
            AND a.created_at >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
            GROUP BY DATE_FORMAT(a.created_at, '%Y-%m')
            ORDER BY month DESC
        """
        
        cursor.execute(trends_query, (provider_id,))
        trends = cursor.fetchall()
        
        # Get top scholarships by applications
        top_scholarships_query = """
            SELECT 
                s.title,
                s.amount,
                COUNT(a.id) as application_count,
                SUM(CASE WHEN a.status = 'APPROVED' THEN 1 ELSE 0 END) as approved_count
            FROM scholarships s
            LEFT JOIN applications a ON s.id = a.scholarship_id
            WHERE s.provider_id = %s
            GROUP BY s.id, s.title, s.amount
            ORDER BY application_count DESC
            LIMIT 5
        """
        
        cursor.execute(top_scholarships_query, (provider_id,))
        top_scholarships = cursor.fetchall()
        
        # Get status distribution
        status_query = """
            SELECT 
                a.status,
                COUNT(*) as count
            FROM applications a
            JOIN scholarships s ON a.scholarship_id = s.id
            WHERE s.provider_id = %s
            GROUP BY a.status
        """
        
        cursor.execute(status_query, (provider_id,))
        status_distribution = cursor.fetchall()
        
        return jsonify({
            'success': True,
            'analytics': {
                'monthly_trends': trends,
                'top_scholarships': top_scholarships,
                'status_distribution': status_distribution
            }
        })
        
    except Exception as e:
        print(f"Error fetching analytics: {e}")
        return jsonify({'success': False, 'message': 'Failed to fetch analytics'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/test-integration')
def test_integration():
    """Test route to verify the integration is working"""
    return jsonify({
        'success': True,
        'message': 'EASECHOLAR integration is working!',
        'features': [
            'Enhanced authentication system',
            'Session-based user management', 
            'Role-based access control',
            'Dashboard data preparation',
            'API endpoints for frontend',
            'Improved error handling'
        ],
        'routes_available': [
            '/ - Landing page',
            '/login - User authentication',
            '/register - User registration',
            '/forgot-password - Password reset',
            '/Students/dashboard.html - Student dashboard',
            '/Provider/dashboard.html - Provider dashboard',
            '/api/auth/status - Check authentication',
            '/api/dashboard/data - Get dashboard data',
            '/create-admin-user - Create admin user'
        ]
    })

@app.route('/debug/provider-status')
@login_required(['PROVIDER'])
def debug_provider_status():
    """Debug endpoint to check provider status"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        user_id = session.get('user_id')
        cursor = connection.cursor(dictionary=True)
        
        # Get user info
        cursor.execute("SELECT id, email, user_type, first_name, last_name FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        # Get provider info
        cursor.execute("SELECT * FROM providers WHERE user_id = %s", (user_id,))
        provider = cursor.fetchone()
        
        # Get scholarships count
        scholarship_count = 0
        if provider:
            cursor.execute("SELECT COUNT(*) as count FROM scholarships WHERE provider_id = %s", (provider['id'],))
            result = cursor.fetchone()
            scholarship_count = result['count'] if result else 0
            
            # Get all scholarships
            cursor.execute("SELECT id, title, scholarship_type, is_active, created_at FROM scholarships WHERE provider_id = %s", (provider['id'],))
            scholarships = cursor.fetchall()
            
            # Convert datetime objects to strings
            for s in scholarships:
                if s.get('created_at'):
                    s['created_at'] = s['created_at'].strftime('%Y-%m-%d %H:%M:%S') if hasattr(s['created_at'], 'strftime') else str(s['created_at'])
            
            # Convert datetime in provider
            if provider.get('created_at'):
                provider['created_at'] = provider['created_at'].strftime('%Y-%m-%d %H:%M:%S') if hasattr(provider['created_at'], 'strftime') else str(provider['created_at'])
            if provider.get('updated_at'):
                provider['updated_at'] = provider['updated_at'].strftime('%Y-%m-%d %H:%M:%S') if hasattr(provider['updated_at'], 'strftime') else str(provider['updated_at'])
        else:
            scholarships = []
        
        return jsonify({
            'success': True,
            'user': user,
            'provider': provider,
            'scholarship_count': scholarship_count,
            'scholarships': scholarships,
            'session_data': {
                'user_id': session.get('user_id'),
                'user_type': session.get('user_type'),
                'email': session.get('email')
            }
        })
        
    except Exception as e:
        print(f"Error in debug endpoint: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

if __name__ == '__main__':
    # Initialize admin user on startup
    try:
        initialize_admin_user()
        print("✓ Admin user initialization completed")
    except Exception as e:
        print(f"⚠ Admin user initialization error: {e}")
    
    # Determine if running in production or development
    import sys
    is_production = '--production' in sys.argv or os.environ.get('FLASK_ENV') == 'production'
    
    if is_production:
        # Production mode - Use waitress server
        from waitress import serve
        
        print("🚀 Starting EASECHOLAR in PRODUCTION mode...")
        print("📧 Test accounts:")
        print("   Student: student@test.com / 12345")
        print("   Provider: provider@test.com / 12345")
        print("   Admin: admin@gmail.com / 12345")
        print("🌐 Server running on port 5000")
        print("⚠️  Debug mode: OFF (Production)")
        
        # Run with waitress (production-ready server)
        serve(app, host='0.0.0.0', port=5000, threads=4)
    else:
        # Development mode - Use Flask development server
        print("🚀 Starting EASECHOLAR in DEVELOPMENT mode...")
        print("📧 Test accounts:")
        print("   Student: student@test.com / 12345")
        print("   Provider: provider@test.com / 12345")
        print("   Admin: admin@gmail.com / 12345")
        print("🌐 Server running at: http://127.0.0.1:5000")
        print("⚠️  To run in production mode, use: python app.py --production")
        
        # Run the application (development only)
        app.run(host='0.0.0.0', port=5000, debug=True)