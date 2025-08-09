# Yarl IT Hub Coordinator Management System - Setup Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- Git
- pip (Python package installer)

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/yarl-coordinator-management.git
cd yarl-coordinator-management
```

### 2. Create Virtual Environment (Recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup
```bash
# Apply migrations
python manage.py migrate

# Create initial data (includes superuser and sample data)
python manage.py setup_initial_data --create-superuser
```

### 5. Run Development Server
```bash
python manage.py runserver
```

### 6. Access the Application
- Open your browser and go to `http://localhost:8000`
- Login with the credentials below

## 🔑 Default Login Credentials

### Admin Account
- **Username**: `mathu`
- **Password**: `yit@2024`
- **Role**: Community Manager (Full Access)

### Coordinator Accounts
- **Batticaloa**: `coord_batticaloa` / `coord123`
- **Ampara**: `coord_ampara` / `coord123`
- **Trincomalee**: `coord_trincomalee` / `coord123`
- **Polonnaruwa**: `coord_polonnaruwa` / `coord123`
- **Anuradhapura**: `coord_anuradhapura` / `coord123`

## 📊 Database Information

### SQLite Database
The project uses SQLite for development, which is included and configured by default:

- **Database File**: `db.sqlite3` (auto-created)
- **Location**: Project root directory
- **Size**: ~320KB with sample data
- **Tables**: 15+ tables including auth, dashboard models, and allauth tables

### Sample Data Included
- 5 Districts (Batticaloa, Ampara, Trincomalee, Polonnaruwa, Anuradhapura)
- 5 District Coordinators
- 3 Sample Initiatives
- 9 Sample Tasks
- 6 Sample Notes
- Admin user with full access

### Database Schema
```sql
-- Main Tables
- auth_user (Django users)
- dashboard_district (Districts)
- dashboard_userprofile (User profiles with roles)
- dashboard_initiative (Projects/Programs)
- dashboard_task (Tasks within initiatives)
- dashboard_note (Meeting notes, updates)
- dashboard_document (File uploads)

-- Additional Tables
- django_session (User sessions)
- allauth_* (Authentication tables)
- django_admin_log (Admin actions)
```

## 🌐 URL Structure (AdminLTE Style)

### Dashboard URLs
- `/` - Main dashboard
- `/dashboard/` - Dashboard home
- `/dashboard/v1/` - Dashboard variant 1
- `/dashboard/v2/` - Dashboard variant 2

### Management URLs
- `/initiatives/` - Initiative management
- `/tasks/` - Task management
- `/notes/` - Notes management
- `/documents/` - Document management

### Organization URLs
- `/districts/` - District management
- `/users/` - User management (admin only)

### Analytics URLs
- `/reports/` - Reports dashboard
- `/charts/` - Charts and visualizations

### Tools URLs
- `/calendar/` - Calendar view
- `/timeline/` - Activity timeline
- `/widgets/` - Widget showcase

### API URLs
- `/api/dashboard-stats/` - Dashboard statistics
- `/api/chart-data/` - Chart data
- `/api/notifications/` - User notifications

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

### Django Settings
Key settings in `coordinator_management/settings.py`:
```python
# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Static Files
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media Files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

## 🚀 Production Deployment

### For PostgreSQL (Production)
1. Install PostgreSQL adapter:
```bash
pip install psycopg2-binary
```

2. Update settings:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'coordinator_management',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Static Files for Production
```bash
python manage.py collectstatic
```

### Environment Setup
```bash
# Set environment variables
export SECRET_KEY='your-production-secret-key'
export DEBUG=False
export ALLOWED_HOSTS='yourdomain.com,www.yourdomain.com'
```

## 📁 Project Structure
```
yarl-coordinator-management/
├── coordinator_management/     # Django project settings
│   ├── settings.py            # Main settings
│   ├── urls.py               # URL configuration
│   └── wsgi.py               # WSGI configuration
├── dashboard/                 # Main application
│   ├── models.py             # Database models
│   ├── views.py              # View functions
│   ├── forms.py              # Django forms
│   ├── admin.py              # Admin interface
│   ├── urls.py               # App URLs
│   └── management/commands/   # Custom commands
├── templates/                 # HTML templates
│   ├── base.html             # Base template
│   ├── account/              # Auth templates
│   └── dashboard/            # Dashboard templates
├── static/                    # Static files
│   ├── css/style.css         # Custom styles
│   ├── js/main.js            # JavaScript
│   └── images/               # Images
├── media/                     # User uploads
├── db.sqlite3                # SQLite database
├── requirements.txt          # Dependencies
├── README.md                 # Documentation
├── SETUP.md                  # This file
└── manage.py                 # Django management
```

## 🔐 Security Configuration

### Production Security
```python
# In production settings
DEBUG = False
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
```

### File Upload Security
- Maximum file size: 10MB
- Allowed extensions: PDF, DOC, DOCX, TXT, JPG, JPEG, PNG, GIF
- Files are validated before upload
- Secure file storage in media directory

## 🧪 Testing

### Run Tests
```bash
python manage.py test
```

### Create Test Data
```bash
python manage.py setup_initial_data
```

### Reset Database
```bash
rm db.sqlite3
python manage.py migrate
python manage.py setup_initial_data --create-superuser
```

## 📊 Features Overview

### ✅ Completed Features
- **Authentication**: Django AllAuth with email login
- **Dashboard**: Statistics, charts, recent activities
- **Initiative Management**: CRUD operations with filtering
- **Task Management**: Progress tracking, status updates
- **Notes System**: Meeting notes, updates with types
- **Document Management**: File upload with validation
- **User Management**: Admin panel for user control
- **District Management**: Multi-district coordination
- **Reports**: Data export and analytics
- **Responsive Design**: Mobile-friendly interface

### 🔄 API Endpoints
- Real-time dashboard statistics
- Chart data for visualizations
- Task status updates via AJAX
- Notification system

### 🎨 UI Features
- AdminLTE-inspired design
- Bootstrap 5 components
- Interactive charts (Chart.js)
- Color-coded status indicators
- Progress bars and widgets
- Responsive navigation

## 🆘 Troubleshooting

### Common Issues

1. **Migration Error**:
```bash
python manage.py makemigrations dashboard
python manage.py migrate
```

2. **Static Files Not Loading**:
```bash
python manage.py collectstatic
```

3. **Permission Denied**:
```bash
chmod +x manage.py
```

4. **Database Locked**:
```bash
# Stop the server and restart
python manage.py runserver
```

### Development Tips
- Use virtual environment for isolation
- Keep DEBUG=True for development
- Use SQLite for development, PostgreSQL for production
- Regular database backups for production
- Monitor error logs in production

## 📞 Support

For technical support or questions:
- **Email**: support@yarlithub.com
- **GitHub Issues**: Create an issue in the repository
- **Documentation**: Check README.md for detailed info

## 📄 License

This project is developed for Yarl IT Hub and is intended for internal use.

---

**Developed for Yarl IT Hub Coordinator Management System**
*Streamlining coordination across 5 districts*
