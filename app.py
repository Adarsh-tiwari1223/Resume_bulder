import os
import io
from flask import Flask, render_template, request, redirect, url_for, session, send_file, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import pdfkit
from gemini_helper import generate_response

load_dotenv()

app = Flask(__name__)
app.secret_key = 'your_secret_key'

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    return redirect(url_for('form'))

@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        data = request.form.to_dict()

        photo = request.files.get('profile_photo')
        if photo and photo.filename:
            filename = secure_filename(photo.filename)
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo.save(photo_path)
            data['photo_path'] = photo_path
        else:
            data['photo_path'] = None

        prompt = f"Write a 3-4 line resume profile summary for {data['name']} with skills: {data['skills']} and job role: {data.get('job_role', '')}."
        data['summary'] = generate_response(prompt)

        session['resume_data'] = data
        return redirect(url_for('select_template'))
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
    return render_template(f'templates/{template}.html', data=data)

@app.route('/download-resume', methods=['GET'])
def download_resume():
    return redirect(url_for('download_pdf'))

@app.route('/download-pdf', methods=['GET'])
def download_pdf():
    print("Download PDF route called")
    data = session.get('resume_data')
    template = session.get('selected_template')
    print("Data and template loaded:", data, template)

    if not data or not template:
        print("Missing data or template")
        return "Missing resume data or template", 400

    rendered_html = render_template(f'templates/{template}.html', data=data)
    print("HTML rendered")

    config = pdfkit.configuration(wkhtmltopdf=r"C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
    print("PDFKit config set")

    pdf = pdfkit.from_string(rendered_html, False, configuration=config)
    print("PDF generated")

    return send_file(
        io.BytesIO(pdf),
        as_attachment=True,
        download_name="resume.pdf",
        mimetype='application/pdf'
    )

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
