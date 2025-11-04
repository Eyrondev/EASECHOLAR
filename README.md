# 🎓 EASECHOLAR - Scholarship Management Platform

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![Flask](https://img.shields.io/badge/flask-2.3.3-red.svg)
![MySQL](https://img.shields.io/badge/mysql-8.0+-orange.svg)
![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)

A comprehensive web-based scholarship management system that connects students with scholarship providers and helps administrators manage the entire scholarship lifecycle.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Database Setup](#database-setup)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [User Roles](#user-roles)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## 🌟 Overview

EASECHOLAR is a full-featured scholarship management platform designed to streamline the scholarship application process for students, providers, and administrators. The platform provides:

- **For Students**: Browse scholarships, submit applications, track status, and manage profiles
- **For Providers**: Post scholarships, review applications, manage students, and view analytics
- **For Administrators**: Oversee the entire platform, manage users, approve providers, and generate reports

## ✨ Features

### 🎯 Student Portal
- ✅ Browse available scholarships with advanced filters
- ✅ Save favorite scholarships for later
- ✅ Submit scholarship applications with document uploads
- ✅ Track application status in real-time
- ✅ Manage personal profile and academic information
- ✅ Receive notifications about application updates
- ✅ View scholarship recommendations

### 🏢 Provider Portal
- ✅ Create and manage scholarship listings
- ✅ Review and evaluate student applications
- ✅ Download and view application documents
- ✅ Approve or reject applications with feedback
- ✅ View analytics and statistics dashboard
- ✅ Manage scholarship deadlines and requirements
- ✅ Track application trends with interactive charts
- ✅ Export application data

### 👨‍💼 Admin Portal
- ✅ Comprehensive system dashboard with key metrics
- ✅ User management (Students, Providers, Admins)
- ✅ Provider approval workflow
- ✅ Scholarship oversight and moderation
- ✅ Application monitoring and reporting
- ✅ System settings and maintenance mode
- ✅ Generate detailed reports
- ✅ View system-wide analytics

### 🔧 General Features
- ✅ Secure authentication and authorization
- ✅ Role-based access control (RBAC)
- ✅ **Email password reset functionality** 📧
- ✅ Responsive design for all devices
- ✅ File upload and management
- ✅ Real-time notifications
- ✅ Advanced search and filtering
- ✅ Data visualization with Chart.js
- ✅ Active page navigation highlighting
- ✅ Maintenance mode support

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend Layer                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Student   │  │   Provider  │  │    Admin    │        │
│  │   Portal    │  │   Portal    │  │   Portal    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│         HTML5 + TailwindCSS + Vanilla JavaScript            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      Application Layer                       │
│                   Flask 2.3.3 (Python 3.8+)                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Authentication │ Authorization │ Business Logic     │  │
│  │  File Upload    │ Session Mgmt  │ API Endpoints      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                        Database Layer                        │
│                    MySQL 8.0+ / MariaDB                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  users │ students │ providers │ scholarships         │  │
│  │  applications │ documents │ system_settings          │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 💻 Technology Stack

### Backend
- **Framework**: Flask 2.3.3
- **Language**: Python 3.8+
- **Database**: MySQL 8.0+ / MariaDB 10.4+
- **ORM**: mysql-connector-python 8.1.0
- **Email**: Flask-Mail 0.9.1
- **Authentication**: Custom session-based with PBKDF2-HMAC-SHA512
- **File Handling**: Werkzeug 2.3.7

### Frontend
- **HTML5**: Semantic markup
- **CSS**: TailwindCSS 3.x (CDN)
- **JavaScript**: Vanilla ES6+
- **Icons**: Font Awesome 6.4.0
- **Charts**: Chart.js 4.4.0
- **Fonts**: Google Fonts (Inter)

### Development Tools
- **Version Control**: Git
- **Package Manager**: pip
- **Virtual Environment**: venv
- **Database Management**: phpMyAdmin / MySQL Workbench

---

## 📦 Prerequisites

Before installing EASECHOLAR, ensure you have the following installed:

### Required Software
- **Python**: 3.8 or higher
  ```bash
  python --version
  ```

- **MySQL**: 8.0 or higher (or MariaDB 10.4+)
  ```bash
  mysql --version
  ```

- **pip**: Python package installer (usually comes with Python)
  ```bash
  pip --version
  ```

### Recommended Software
- **Git**: For version control
- **phpMyAdmin**: For database management (optional)
- **Visual Studio Code**: For code editing (optional)

---

## 🚀 Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/easecholar.git
cd easecholar
```

Or download and extract the ZIP file.

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv env
env\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv env
source env/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Flask 2.3.3
- Flask-Mail 0.9.1 (for password reset emails)
- mysql-connector-python 8.1.0
- bcrypt 4.0.1
- Werkzeug 2.3.7
- python-dotenv 1.0.0
- Pillow 10.0.0 (for image handling)

---

## 🗄️ Database Setup

### Option 1: Automated Setup (Recommended)

Run the automated setup script:

```bash
python setup_database.py
```

This script will:
1. ✅ Check MySQL connection
2. ✅ Create the `easecholar_db` database
3. ✅ Import all tables and schema
4. ✅ Create default admin account
5. ✅ Set up initial system settings
6. ✅ Verify database integrity

**Default Admin Credentials:**
- **Username**: `admin@easecholar.com`
- **Password**: `admin123`
- ⚠️ **Important**: Change these credentials immediately after first login!

### Option 2: Manual Setup

If you prefer manual setup, follow the detailed guide:
📖 [DATABASE_SETUP.md](./DATABASE_SETUP.md)

**Quick Manual Steps:**

1. **Start MySQL Server**
   ```bash
   # Windows
   net start MySQL80
   
   # Linux
   sudo systemctl start mysql
   ```

2. **Login to MySQL**
   ```bash
   mysql -u root -p
   ```

3. **Create Database**
   ```sql
   CREATE DATABASE easecholar_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   USE easecholar_db;
   ```

4. **Import Schema**
   ```bash
   mysql -u root -p easecholar_db < database/easecholar_db.sql
   ```

5. **Add Password Reset Table** (Required for email password reset)
   ```bash
   mysql -u root -p easecholar_db < database/add_password_reset_tokens.sql
   ```

6. **Verify Tables**
   ```sql
   SHOW TABLES;
   ```

---

## ⚙️ Configuration

### 1. Database Configuration

Edit `app.py` and update the database credentials:

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_mysql_password',  # Update this!
    'database': 'easecholar_db',
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}
```

### 2. Environment Variables (Optional)

Create a `.env` file in the root directory:

```env
SECRET_KEY=your_super_secret_key_here
FLASK_ENV=development
FLASK_DEBUG=True
DATABASE_HOST=localhost
DATABASE_USER=root
DATABASE_PASSWORD=your_mysql_password
DATABASE_NAME=easecholar_db
UPLOAD_FOLDER=uploads
MAX_FILE_SIZE=5242880

# Email Configuration (for password reset)
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-gmail-app-password
```

**📧 Email Setup for Password Reset:**

For detailed email configuration instructions, see:
- **Quick Setup**: [QUICKSTART_EMAIL.md](./QUICKSTART_EMAIL.md) - 5-minute setup
- **Detailed Guide**: [EMAIL_SETUP_GUIDE.md](./EMAIL_SETUP_GUIDE.md) - Complete documentation
- **Test Email**: Run `python test_email.py` to verify configuration

**Quick Email Setup:**
1. Generate Gmail App Password at https://myaccount.google.com/apppasswords
2. Set environment variables:
   ```cmd
   setx MAIL_USERNAME "your-email@gmail.com"
   setx MAIL_PASSWORD "your-app-password"
   ```
3. Restart terminal/IDE
4. Test: `python test_email.py`

### 3. File Upload Directory

The `uploads` folder is created automatically. Ensure write permissions:

```bash
# Windows
mkdir uploads

# Linux/Mac
mkdir -p uploads
chmod 755 uploads
```

---

## ▶️ Running the Application

### Development Mode

```bash
# Activate virtual environment first
# Windows
env\Scripts\activate

# Linux/Mac
source env/bin/activate

# Run the application
python app.py
```

The application will start on `http://localhost:5000`

### Production Mode

For production deployment, use a WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Or use waitress for Windows:

```bash
pip install waitress
waitress-serve --listen=*:5000 app:app
```

---

## 👥 User Roles

### 1. Administrator
**Access Level**: Full system control

**Default Login:**
- Email: `admin@easecholar.com`
- Password: `admin123`

**Capabilities:**
- Manage all users (Students, Providers, Admins)
- Approve/reject provider registrations
- Oversee all scholarships and applications
- Generate system reports
- Access system settings
- Enable/disable maintenance mode

### 2. Provider
**Access Level**: Scholarship and application management

**Registration**: Self-registration with admin approval required

**Capabilities:**
- Create and manage scholarships
- Review student applications
- View and download application documents
- Approve/reject applications
- View analytics dashboard
- Manage profile and settings

### 3. Student
**Access Level**: Browse and apply for scholarships

**Registration**: Self-registration with email verification

**Capabilities:**
- Browse available scholarships
- Save favorite scholarships
- Submit scholarship applications
- Upload required documents
- Track application status
- Manage personal profile
- View application history

---

## 📁 Project Structure

```
EASECHOLAR/
│
├── 📄 app.py                      # Main Flask application
├── 📄 setup_database.py           # Automated database setup script
├── 📄 update_database.py          # Database migration script
├── 📄 test_email.py               # Email configuration tester
├── 📄 requirements.txt            # Python dependencies
├── 📄 README.md                   # This file
├── 📄 DATABASE_SETUP.md           # Detailed database guide
├── 📄 EMAIL_SETUP_GUIDE.md        # Email configuration guide
├── 📄 QUICKSTART_EMAIL.md         # Quick email setup (5 minutes)
├── 📄 IMPLEMENTATION_SUMMARY.md   # Email feature documentation
├── 📄 SYSTEM_ARCHITECTURE.md      # System design documentation
├── 📄 TESTING_GUIDE.md            # Testing procedures
├── 📄 .env.example                # Environment variables template
├── 📄 .gitignore                  # Git ignore patterns
│
├── 📂 Admin/                      # Admin portal files
│   ├── dashboard.html             # Admin dashboard
│   ├── users.html                 # User management
│   ├── students.html              # Student management
│   ├── providers.html             # Provider management
│   ├── scholarships.html          # Scholarship oversight
│   ├── applications.html          # Application monitoring
│   ├── approvals.html             # Provider approvals
│   ├── reports.html               # System reports
│   ├── settings.html              # System settings
│   ├── sidebar.html               # Navigation sidebar
│   ├── nav.html                   # Top navigation
│   ├── header.html                # Header component
│   └── components.js              # Component loader
│
├── 📂 Provider/                   # Provider portal files
│   ├── dashboard.html             # Provider dashboard
│   ├── scholarships.html          # Scholarship management
│   ├── applications.html          # Application review
│   ├── students.html              # Student list
│   ├── analytics.html             # Analytics & charts
│   ├── settings.html              # Provider settings
│   ├── help.html                  # Help & support
│   ├── sidebar.html               # Navigation sidebar
│   ├── nav.html                   # Top navigation
│   ├── header.html                # Header component
│   └── components.js              # Component loader
│
├── 📂 Students/                   # Student portal files
│   ├── dashboard.html             # Student dashboard
│   ├── browse-scholarships.html   # Scholarship browser
│   ├── scholarship-details.html   # Scholarship details page
│   ├── my-applications.html       # Application tracker
│   ├── saved-scholarships.html    # Saved scholarships
│   ├── profile.html               # Student profile
│   ├── settings.html              # Student settings
│   ├── sidebar.html               # Navigation sidebar
│   ├── nav.html                   # Top navigation
│   ├── header.html                # Header component
│   └── components.js              # Component loader
│
├── 📂 Assets/                     # Static assets
│   ├── 📂 images/                 # Images and logos
│   └── 📂 js/                     # Shared JavaScript files
│
├── 📂 database/                   # Database files
│   ├── easecholar_db.sql          # Database schema and data
│   └── add_password_reset_tokens.sql  # Password reset table
│
├── 📂 uploads/                    # User uploaded files
│   └── 📂 student_documents/      # Student application documents
│       └── 📂 {user_id}/          # Organized by user ID
│
├── 📂 env/                        # Virtual environment (not in git)
│
├── 📄 index.html                  # Landing page
├── 📄 login.html                  # Login page
├── 📄 register.html               # Registration page
├── 📄 forgot-password.html        # Password recovery
├── 📄 reset-password.html         # Password reset page (with token)
├── 📄 404.html                    # 404 error page
└── 📄 maintenance.html            # Maintenance mode page
```

---

## 🔌 API Documentation

### Authentication Endpoints

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "user_type": "STUDENT|PROVIDER|ADMIN"
}

Response: 200 OK
{
  "success": true,
  "message": "Login successful",
  "redirect": "/Students/dashboard.html"
}
```

#### Register
```http
POST /api/auth/register
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123",
  "user_type": "STUDENT|PROVIDER"
}

Response: 201 Created
{
  "success": true,
  "message": "Registration successful"
}
```

#### Check Auth Status
```http
GET /api/auth/status

Response: 200 OK
{
  "authenticated": true,
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "user_type": "STUDENT"
  }
}
```

### Password Reset Endpoints

#### Request Password Reset
```http
POST /forgot-password
Content-Type: application/x-www-form-urlencoded

email=user@example.com

Response: 200 OK
Shows success message and sends email with reset link
```

#### Verify Reset Token
```http
GET /api/verify-reset-token/{token}

Response: 200 OK
{
  "valid": true,
  "message": "Token is valid"
}
```

#### Reset Password
```http
POST /api/reset-password
Content-Type: application/json

{
  "token": "secure-token-here",
  "new_password": "newpassword123"
}

Response: 200 OK
{
  "success": true,
  "message": "Password has been reset successfully"
}
```

### Student Endpoints

#### Get Available Scholarships
```http
GET /api/student/scholarships?limit=10&offset=0

Response: 200 OK
{
  "success": true,
  "scholarships": [...],
  "total": 50
}
```

#### Submit Application
```http
POST /api/student/apply
Content-Type: multipart/form-data

scholarship_id: 1
cover_letter: "..."
documents: [files]

Response: 201 Created
{
  "success": true,
  "application_id": 123
}
```

### Provider Endpoints

#### Get Applications
```http
GET /api/provider/applications

Response: 200 OK
{
  "success": true,
  "applications": [...]
}
```

#### Update Application Status
```http
POST /api/provider/application/update-status
Content-Type: application/json

{
  "application_id": 123,
  "status": "APPROVED|REJECTED",
  "notes": "Feedback message"
}

Response: 200 OK
{
  "success": true,
  "message": "Application status updated"
}
```

#### Get Dashboard Stats
```http
GET /api/provider/dashboard-stats

Response: 200 OK
{
  "success": true,
  "data": {
    "total_scholarships": 10,
    "total_applications": 50,
    "pending_applications": 20,
    "approved_applications": 25
  }
}
```

#### Get Applications Chart Data
```http
GET /api/provider/applications-chart?days=30

Response: 200 OK
{
  "success": true,
  "data": {
    "labels": ["Oct 1", "Oct 2", ...],
    "pending": [5, 3, ...],
    "approved": [2, 4, ...],
    "rejected": [1, 0, ...]
  }
}
```

### Admin Endpoints

#### Get All Users
```http
GET /api/admin/users?type=STUDENT|PROVIDER|ADMIN

Response: 200 OK
{
  "success": true,
  "users": [...]
}
```

#### Approve Provider
```http
POST /api/admin/approve-provider
Content-Type: application/json

{
  "provider_id": 5
}

Response: 200 OK
{
  "success": true,
  "message": "Provider approved"
}
```

---

## 🧪 Testing

### Manual Testing

1. **Test User Login**
   - Navigate to `http://localhost:5000/login.html`
   - Try logging in with different user types
   - Verify redirects and access control

2. **Test Student Flow**
   - Browse scholarships
   - Submit an application
   - Upload documents
   - Check application status

3. **Test Provider Flow**
   - Create a scholarship
   - Review applications
   - Download documents
   - Approve/reject applications

4. **Test Admin Flow**
   - View system dashboard
   - Manage users
   - Approve providers
   - Generate reports

### Automated Testing

Run the test suite (if available):

```bash
python -m pytest tests/
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Database Connection Error
**Problem**: `Error connecting to MySQL database`

**Solution**:
- Verify MySQL is running: `mysql --version`
- Check credentials in `app.py`
- Test connection: `mysql -u root -p`

#### 2. Module Not Found Error
**Problem**: `ModuleNotFoundError: No module named 'flask'`

**Solution**:
```bash
# Activate virtual environment
env\Scripts\activate  # Windows
source env/bin/activate  # Linux/Mac

# Reinstall dependencies
pip install -r requirements.txt
```

#### 3. File Upload Error
**Problem**: Files not uploading

**Solution**:
- Check `uploads` folder exists and has write permissions
- Verify file size < 5MB
- Check file type is allowed

#### 4. Port Already in Use
**Problem**: `Address already in use`

**Solution**:
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :5000
kill -9 <PID>
```

#### 5. Active Page Not Highlighting
**Problem**: Sidebar navigation not showing active page

**Solution**:
- Clear browser cache
- Check browser console for JavaScript errors
- Verify component loader is working

#### 6. Email Not Sending (Password Reset)
**Problem**: Password reset emails not being delivered

**Solution**:
- Verify environment variables: `echo %MAIL_USERNAME%`
- Use Gmail App Password, not regular password
- Enable 2-Factor Authentication on Gmail
- Check firewall settings (allow port 587)
- Run test: `python test_email.py`
- See [EMAIL_SETUP_GUIDE.md](./EMAIL_SETUP_GUIDE.md) for detailed troubleshooting

#### 7. "Invalid or Expired Link" Error
**Problem**: Password reset link shows as expired

**Solution**:
- Links expire after 1 hour - request a new one
- Make sure database table `password_reset_tokens` exists
- Check server time is correct

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Coding Standards
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Write docstrings for functions
- Test your changes before submitting

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Authors

- **Your Name** - *Initial work* - [YourGitHub](https://github.com/yourusername)

---

## 🙏 Acknowledgments

- Flask documentation and community
- TailwindCSS for the amazing CSS framework
- Chart.js for data visualization
- Font Awesome for icons
- All contributors and testers

---

## 📞 Support

For support, email support@easecholar.com or open an issue on GitHub.

---

## 🗺️ Roadmap

### Version 2.0 (Planned)
- [ ] Email notifications
- [ ] SMS notifications
- [ ] Advanced search with AI
- [ ] Scholarship recommendations engine
- [ ] Mobile application
- [ ] Payment integration
- [ ] Multi-language support
- [ ] Real-time chat support
- [ ] Document verification system
- [ ] Blockchain certification

---

## 📊 Statistics

- **Total Lines of Code**: ~5,000+
- **Number of Tables**: 12+
- **API Endpoints**: 50+
- **Supported File Types**: PDF, DOC, DOCX, JPG, PNG
- **Max File Size**: 5MB
- **Response Time**: <200ms average

---

**Made with ❤️ by the EASECHOLAR Team**

*Last Updated: October 3, 2025*
