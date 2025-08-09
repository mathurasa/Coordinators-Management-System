# Yarl IT Hub Coordinator Management System

A comprehensive Django-based management system for coordinating initiatives across 5 districts, designed for the Yarl IT Hub organization.

## Features

### Admin Dashboard (Community Manager)
- View all district coordinators and their profiles
- Add/edit/remove initiatives
- Assign tasks to coordinators
- View status updates and progress by district
- Download/export reports (CSV/PDF)
- View all notes/comments
- Filter by initiative, date, status

### Coordinator Portal
- View personal dashboard for assigned district
- Add/update task status
- Maintain notes for each initiative
- Upload documents/images
- To-do list with deadlines

### Key Functionalities
- **Initiative Management**: Track ongoing and completed initiatives with filtering by district and type
- **Task Tracker**: Assign tasks with priorities, deadlines, and progress tracking
- **Notes & Document Center**: Meeting notes, workshop summaries, and file attachments
- **Permission-Based Access**: Role-based access control for admins and coordinators

## Tech Stack

- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Backend**: Python, Django 5.2.5
- **Database**: SQLite (Development), PostgreSQL (Production ready)
- **Authentication**: Django AllAuth
- **File Handling**: Pillow for image processing

## Installation & Setup

### Prerequisites
- Python 3.10 or higher
- pip (Python package installer)

### Quick Start

1. **Clone the repository**
```bash
git clone <repository-url>
cd "Coordinators Management System"
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run migrations**
```bash
python manage.py migrate
```

4. **Set up initial data (includes superuser and sample data)**
```bash
python manage.py setup_initial_data --create-superuser
```

5. **Run the development server**
```bash
python manage.py runserver
```

6. **Access the application**
- Open your browser and go to `http://localhost:8000`
- Login with the credentials below

## Default Login Credentials

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

## Project Structure

```
Coordinators Management System/
├── coordinator_management/     # Main Django project
│   ├── settings.py            # Django settings
│   ├── urls.py               # URL configuration
│   └── wsgi.py               # WSGI configuration
├── dashboard/                 # Main application
│   ├── models.py             # Database models
│   ├── views.py              # View functions
│   ├── forms.py              # Django forms
│   ├── admin.py              # Admin interface
│   ├── urls.py               # App URLs
│   └── management/commands/   # Custom management commands
├── templates/                 # HTML templates
│   ├── base.html             # Base template
│   ├── account/              # Authentication templates
│   └── dashboard/            # Dashboard templates
├── static/                    # Static files
│   ├── css/                  # Stylesheets
│   ├── js/                   # JavaScript files
│   └── images/               # Image assets
├── media/                     # User uploaded files
├── requirements.txt           # Python dependencies
└── README.md                 # This file
```

## Database Models

### Core Models
- **District**: Represents the 5 districts (Batticaloa, Ampara, Trincomalee, Polonnaruwa, Anuradhapura)
- **UserProfile**: Extended user model with roles and district assignments
- **Initiative**: Main projects/programs managed by coordinators
- **Task**: Individual tasks within initiatives with progress tracking
- **Note**: Meeting notes, updates, and documentation
- **Document**: File uploads related to initiatives and tasks

### User Roles
- **Admin (Community Manager)**: Full CRUD access to all data
- **Coordinator**: View/edit only their district's data
- **Read-only** (Future): View-only access to dashboards

## Key Features in Detail

### Dashboard
- Real-time statistics and KPIs
- Recent activities timeline
- Quick action buttons
- District overview (admin only)

### Task Management
- Priority levels (Low, Medium, High, Urgent)
- Status tracking (Not Started, In Progress, Completed, On Hold)
- Progress percentage with visual indicators
- Overdue task highlighting
- AJAX-powered status updates

### Initiative Management
- Multiple initiative types (Training, Workshop, Mentorship, etc.)
- Budget tracking
- KPI target setting
- Start and end date management
- Status tracking with color-coded indicators

### Notes System
- Multiple note types (Meeting, Workshop, General, Milestone, Feedback)
- Public/private visibility settings
- Rich text content
- Initiative and task associations

### Document Management
- File upload with validation
- Support for PDF, DOC, DOCX, TXT, and image formats
- File size validation (10MB limit)
- Document preview functionality
- Secure file storage

### Security Features
- Role-based access control
- CSRF protection
- File upload validation
- District-based data isolation
- Secure authentication with Django AllAuth

## Customization

### Adding New Districts
1. Use Django admin to add new districts
2. Create coordinator users and assign to districts
3. Update any hardcoded district references if needed

### Adding New Initiative Types
Update the `TYPE_CHOICES` in `dashboard/models.py`:
```python
TYPE_CHOICES = [
    ('training', 'Training Program'),
    ('workshop', 'Workshop'),
    ('your_new_type', 'Your New Type'),
    # ... existing choices
]
```

### Custom Management Commands
The project includes a custom management command for initial setup:
```bash
python manage.py setup_initial_data --create-superuser
```

## Development Guidelines

### Frontend
- Bootstrap 5 for responsive design
- Custom CSS for branding and specific styling
- jQuery for enhanced interactivity
- Bootstrap Icons for consistent iconography

### Backend
- Django best practices followed
- Model-View-Template (MVT) architecture
- Class-based and function-based views
- Custom forms with validation
- Comprehensive admin interface

### Database
- SQLite for development (included)
- PostgreSQL ready for production
- Proper relationships and constraints
- Indexed fields for performance

## Production Deployment

### Environment Variables
Create a `.env` file with:
```
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com
DATABASE_URL=postgres://user:pass@localhost/dbname
```

### Static Files
```bash
python manage.py collectstatic
```

### Recommended Hosting
- **Render**: Easy Django deployment
- **Railway**: Simple and fast
- **Vercel**: For serverless deployment
- **DigitalOcean**: VPS with more control

## API Endpoints

### Dashboard API
- `GET /api/dashboard-stats/`: Real-time dashboard statistics

### Task Management API
- `POST /tasks/<id>/update-status/`: Update task status via AJAX

## Browser Support
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is developed for Yarl IT Hub and is intended for internal use.

## Support

For technical support or questions about the system:
- Contact: Technical Team at Yarl IT Hub
- Email: support@yarlithub.com

## Changelog

### Version 1.0.0 (Current)
- Initial release with core functionality
- District management system
- Initiative and task tracking
- Notes and document management
- Role-based access control
- Responsive dashboard interface

## Future Enhancements

### Phase 2 (Planned)
- Advanced reporting and analytics
- Email notifications
- Calendar integration
- Mobile app companion

### Phase 3 (Future)
- Activity logs and audit trails
- Advanced file management
- Integration with external tools
- API for third-party integrations

---

**Developed for Yarl IT Hub Coordinator Management System**
*Streamlining coordination across 5 districts*
