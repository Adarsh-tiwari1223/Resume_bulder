import os
import io
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, request, redirect, url_for, session, send_file, jsonify, abort
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pdfkit
import re
from gemini_helper import generate_response

# Load environment variables
load_dotenv()

# Configure logging
if not os.path.exists('logs'):
    os.makedirs('logs')

file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)

# Initialize Flask app
app = Flask(__name__)

# Configure logging
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Resume Builder startup')

# Ensure all required environment variables are set
required_env_vars = ['SECRET_KEY', 'GEMINI_API_KEY']
for var in required_env_vars:
    if not os.getenv(var):
        app.logger.error(f'Missing required environment variable: {var}')
        raise RuntimeError(f'Missing required environment variable: {var}')

# Security Configuration
app.secret_key = os.getenv('SECRET_KEY', os.urandom(24).hex())
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=timedelta(minutes=30),
    MAX_CONTENT_LENGTH=16 * 1024 * 1024  # 16MB max file size
)

# File Upload Configuration
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', os.path.join(app.root_path, 'static', 'uploads'))
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'}

# Ensure upload directory exists
try:
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.logger.info(f'Upload directory configured: {UPLOAD_FOLDER}')
except Exception as e:
    app.logger.warning(f'Could not create upload directory: {e}')
    # Fallback to temporary directory if needed
    UPLOAD_FOLDER = os.path.join('/tmp', 'uploads')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    return render_template('home.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    pattern = r'^\+?[1-9][0-9]{7,14}$'
    return re.match(pattern, phone) is not None

def clean_filename(filename):
    # Generate timestamp-based unique filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
    clean_name = secure_filename(filename)
    return timestamp + clean_name

@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(error):
    return 'File is too large. Maximum size is 16MB.', 413

@app.route('/upload-resume', methods=['GET', 'POST'])
def upload_resume():
    if request.method == 'POST':
        if 'resume_file' not in request.files:
            return render_template('upload_resume.html', error="No file selected.")
            
        uploaded_file = request.files['resume_file']
        if uploaded_file.filename == '':
            return render_template('upload_resume.html', error="No file selected.")
            
        if not allowed_file(uploaded_file.filename):
            return render_template('upload_resume.html', 
                error=f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}")

        try:
            filename = clean_filename(uploaded_file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(file_path)

            # TODO: Implement resume parsing logic here
            # Clean up old files
            cleanup_old_files(app.config['UPLOAD_FOLDER'], max_files=10)

            return redirect(url_for('form'))
        except Exception as e:
            app.logger.error(f"File upload error: {str(e)}")
            return render_template('upload_resume.html', 
                error="An error occurred while uploading the file. Please try again.")

    return render_template('upload_resume.html')

def cleanup_old_files(directory, max_files=10):
    try:
        files = [os.path.join(directory, f) for f in os.listdir(directory) 
                 if os.path.isfile(os.path.join(directory, f))]
        files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        
        for old_file in files[max_files:]:
            os.remove(old_file)
    except Exception as e:
        app.logger.error(f"Cleanup error: {str(e)}")

def process_form_data(form_data, files):
    """Process and validate form data"""
    data = {}
    
    # Process basic information
    for field in ['name', 'email', 'phone', 'address', 'linkedin']:
        data[field] = form_data.get(field, '').strip()
    
    # Validate required fields
    if not all([data['name'], data['email'], data['phone']]):
        raise ValueError("Please fill all required fields.")
    
    # Validate email and phone
    if not validate_email(data['email']):
        raise ValueError("Please enter a valid email address.")
    
    if not validate_phone(data['phone']):
        raise ValueError("Please enter a valid phone number.")
    
    # Process education entries
    education_data = []
    course_names = form_data.getlist('course_name')
    institution_names = form_data.getlist('institution_name')
    edu_froms = form_data.getlist('edu_from')
    edu_tos = form_data.getlist('edu_to')
    
    for i in range(len(course_names)):
        if course_names[i] and institution_names[i] and edu_froms[i] and edu_tos[i]:
            education_data.append({
                'course_name': course_names[i],
                'institution_name': institution_names[i],
                'edu_from': edu_froms[i],
                'edu_to': edu_tos[i]
            })
    
    data['education'] = education_data
    
    # Process skills
    data['skills_list'] = [skill.strip() for skill in form_data.getlist('skills') if skill.strip()]
    
    # Process other fields
    for field in ['certifications', 'job_role', 'job_summary', 'projects']:
        data[field] = form_data.get(field, '').strip()
    
    # Handle profile photo
    photo = files.get('profile_photo')
    if photo and photo.filename:
        if not allowed_file(photo.filename):
            raise ValueError(f"Invalid file type for photo. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}")
        
        filename = clean_filename(photo.filename)
        photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        photo.save(photo_path)
        data['photo_path'] = photo_path
    else:
        data['photo_path'] = None
    
    return data

@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        try:
            data = process_form_data(request.form, request.files)

            # Debug logging for name and phone
            app.logger.info(f"Form data - Name: {data['name']}, Phone: {data['phone']}")

            # Generate AI summary using skills list instead of raw skills field
            skills_text = ", ".join(data['skills_list']) if data['skills_list'] else ""
            prompt = f"Write a 3-4 line professional resume summary for {data['name']} with skills: {skills_text} and job role: {data.get('job_role', '')}."
            
            try:
                data['summary'] = generate_response(prompt)
            except Exception as e:
                app.logger.error(f"AI summary generation error: {str(e)}")
                data['summary'] = "" # Fallback to empty summary on error
            
            # Store in session with expiry
            session['resume_data'] = data
            session.modified = True
            
            return redirect(url_for('select_template'))
            
        except ValueError as e:
            # Handle validation errors
            return render_template('form.html', error=str(e), data=request.form)
        except Exception as e:
            # Handle unexpected errors
            app.logger.error(f"Form processing error: {str(e)}")
            return render_template('form.html', 
                error="An error occurred while processing your form. Please try again.",
                data=request.form)
    else:
        # GET request handling
        prefilled_data = session.get('prefilled_data')
        if prefilled_data:
            # Clear prefilled data after use
            session.pop('prefilled_data', None)
            session.modified = True
            return render_template('form.html', data=prefilled_data)
            
        return render_template('form.html')

@app.route('/select-template', methods=['GET', 'POST'])
def select_template():
    if request.method == 'POST':
        session['selected_template'] = request.form.get('template')
        return redirect(url_for('preview_resume'))
    return render_template('select_template.html')

@app.route('/preview-resume')
def preview_resume():
    data = session.get('resume_data')
    template = session.get('selected_template')
    if not data or not template:
        return redirect(url_for('form'))
    return render_template('preview_resume_wrapper.html', data=data)

@app.route('/download-resume', methods=['GET'])
def download_resume():
    return redirect(url_for('download_pdf'))

def get_wkhtmltopdf_path():
    # Check common installation paths
    paths = [
        r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe",
        r"C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe",
        "/usr/local/bin/wkhtmltopdf",
        "/usr/bin/wkhtmltopdf"
    ]
    
    for path in paths:
        if os.path.exists(path):
            return path
            
    return None

@app.route('/download-pdf', methods=['GET'])
def download_pdf():
    try:
        data = session.get('resume_data')
        template = session.get('selected_template')

        if not data or not template:
            app.logger.error("Missing resume data or template")
            return "Please fill out the resume form first.", 400

        # Validate template name to prevent directory traversal
        if not re.match(r'^template[0-9]+$', template):
            app.logger.error(f"Invalid template name: {template}")
            return "Invalid template selected.", 400

        template_path = f'templates/{template}.html'
        if not os.path.exists(os.path.join(app.root_path, 'templates', 'templates', f'{template}.html')):
            app.logger.error(f"Template file not found: {template_path}")
            return "Selected template not found.", 404

        rendered_html = render_template(f'templates/{template}.html', data=data)

        wkhtmltopdf_path = get_wkhtmltopdf_path()
        if not wkhtmltopdf_path:
            app.logger.error("wkhtmltopdf not found in system")
            return "PDF generation is currently unavailable. Please contact support.", 503

        config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
        
        options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': 'UTF-8',
            'no-outline': None
        }

        pdf = pdfkit.from_string(rendered_html, False, options=options, configuration=config)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"resume_{timestamp}.pdf"

        return send_file(
            io.BytesIO(pdf),
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )

    except Exception as e:
        app.logger.error(f"PDF generation error: {str(e)}")
        return "An error occurred while generating the PDF. Please try again.", 500

@app.route('/suggest', methods=['POST'])
def suggest():
    prompt = request.json.get('prompt')
    if not prompt:
        return jsonify({"error": "Prompt is missing."}), 400
    try:
        reply = generate_response(prompt)
        return jsonify({"response": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
