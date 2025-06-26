# Resume Builder

A Flask-based web application for creating professional resumes with multiple templates and AI-powered summary generation.

## Features

- Multiple professional resume templates
- AI-powered resume summary generation
- PDF download functionality
- Form validation and error handling
- File upload support for profile photos
- Session management and security features

## Prerequisites

- Python 3.8 or higher
- wkhtmltopdf (for PDF generation)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd resume-builder
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. Install the required packages:
```bash
pip install -r requirement.txt
```

4. Install wkhtmltopdf:
- Windows: Download and install from https://wkhtmltopdf.org/downloads.html
- Linux: `sudo apt-get install wkhtmltopdf`
- Mac: `brew install wkhtmltopdf`

## Configuration

1. Create a `.env` file in the project root with the following variables:
```env
SECRET_KEY=your_secret_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

2. Make sure the following directories exist:
```bash
static/uploads/
logs/
```

## Running the Application

1. Start the Flask development server:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

## Security Features

- Session management with secure cookies
- File upload validation
- Input sanitization
- Error logging
- Maximum file size limits
- Secure filename handling

## Maintenance

- Log files are automatically rotated (max 10MB per file)
- Old uploaded files are automatically cleaned up
- Session timeout after 30 minutes of inactivity

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.