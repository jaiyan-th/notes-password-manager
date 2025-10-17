# SecureWebApp

A secure Flask-based web application for personal note-taking and password management with encrypted storage and user authentication.

## Features

### 🔐 User Authentication
- Secure user registration and login
- Password strength validation
- Session management with 30-minute timeout
- Bcrypt password hashing

### 📝 Notes Management
- Create, read, update, and delete personal notes
- Search functionality across notes
- Character limit validation (5000 chars)
- Chronological ordering with timestamps

### 🔑 Password Manager
- Secure password storage with AES encryption
- Password reveal/hide functionality
- Built-in password generator
- Copy-to-clipboard functionality
- User-specific encryption keys

### 🎨 User Interface
- Responsive Bootstrap design
- Mobile-friendly interface
- Real-time password strength indicator
- Flash message system for user feedback
- Intuitive navigation and dashboard

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Flask-Login
- **Forms**: WTForms with validation
- **Encryption**: Cryptography library (Fernet)
- **Frontend**: Bootstrap 5, Font Awesome
- **Testing**: Pytest

## Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python run.py
   ```

4. **Open your browser** and go to `http://localhost:5000`

## Project Structure

```
SecureWebApp/
├── app.py                 # Main Flask application
├── models.py             # Database models
├── auth.py               # Authentication routes
├── notes.py              # Notes management routes
├── passwords.py          # Password management routes
├── config.py             # Configuration settings
├── run.py                # Application runner
├── init_db.py            # Database initialization
├── test_app.py           # Test suite
├── requirements.txt      # Python dependencies
├── utils/
│   ├── forms.py          # WTForms form definitions
│   └── security.py       # Security utilities
└── templates/            # HTML templates
    ├── base.html         # Base template
    ├── login.html        # Login page
    ├── register.html     # Registration page
    ├── dashboard.html    # Main dashboard
    ├── notes.html        # Notes listing
    ├── passwords.html    # Password manager
    └── ...               # Additional templates
```

## Security Features

### Password Security
- User passwords hashed with bcrypt
- Stored passwords encrypted with Fernet (AES)
- User-specific encryption keys
- Password strength validation

### Data Protection
- User data isolation
- CSRF protection on forms
- Session-based authentication
- Secure password reveal functionality

### Input Validation
- Server-side form validation
- XSS prevention
- SQL injection protection via ORM
- Content length limits

## Usage

### Getting Started
1. Register a new account with a valid email and strong password
2. Log in to access your personal dashboard
3. Start creating notes or storing passwords securely

### Managing Notes
- Click "New Note" to create a note
- Use the search bar to find specific notes
- Click on any note title to view full content
- Edit or delete notes as needed

### Managing Passwords
- Click "Add Password" to store a new password
- Use the password generator for strong passwords
- Click the eye icon to reveal stored passwords
- Copy usernames and passwords with one click

## Configuration

### Environment Variables
- `SECRET_KEY`: Flask secret key (change in production)
- `DATABASE_URL`: Database connection string
- `FLASK_ENV`: Environment (development/production)
- `MASTER_KEY`: Master key for password encryption

### Database
The application uses SQLite by default. For production, configure a different database via `DATABASE_URL`.

## Testing

Run the test suite:
```bash
pytest test_app.py
```

Or run basic tests:
```bash
python test_app.py
```

## Development

### Adding New Features
1. Create new routes in appropriate blueprint files
2. Add corresponding templates in the `templates/` directory
3. Update forms in `utils/forms.py` if needed
4. Add tests in `test_app.py`

### Database Changes
1. Modify models in `models.py`
2. Run database initialization: `python init_db.py reset`

## Security Considerations

### For Production Use
1. Change the `SECRET_KEY` to a secure random value
2. Use a production database (PostgreSQL, MySQL)
3. Enable HTTPS
4. Set up proper logging and monitoring
5. Configure environment variables securely
6. Regular security updates

### Password Storage
- User passwords are hashed with bcrypt (irreversible)
- Stored passwords are encrypted with AES (reversible with user key)
- Each user has a unique encryption key derived from their ID
- Master key should be kept secure and rotated regularly

## License

This project is for educational and personal use. Please ensure compliance with applicable security and privacy regulations when deploying.

## Support

For issues or questions:
1. Check the test suite for examples
2. Review the code comments for implementation details
3. Ensure all dependencies are properly installed
4. Verify database initialization completed successfully