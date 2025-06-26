import pytest
from app import app, get_wkhtmltopdf_path
from flask import session
import os

@pytest.fixture
def sample_resume_data():
    return {
        'name': 'John Doe',
        'email': 'john@example.com',
        'phone': '+1234567890',
        'address': '123 Test St',
        'linkedin': 'https://linkedin.com/in/johndoe',
        'skills_list': ['Python', 'Flask', 'Testing'],
        'education': [{
            'course_name': 'Computer Science',
            'institution_name': 'Test University',
            'edu_from': '2020-01',
            'edu_to': '2024-01'
        }],
        'summary': 'Experienced software developer with strong testing background'
    }

def test_wkhtmltopdf_path():
    path = get_wkhtmltopdf_path()
    if os.name == 'nt':  # Windows
        assert path is None or path.endswith('wkhtmltopdf.exe')
    else:  # Unix-like
        assert path is None or path.endswith('wkhtmltopdf')

def test_download_pdf_without_data(client):
    response = client.get('/download-pdf')
    assert response.status_code == 400
    assert b'Please fill out the resume form first' in response.data

def test_download_pdf_invalid_template(client, sample_resume_data):
    with client.session_transaction() as sess:
        sess['resume_data'] = sample_resume_data
        sess['selected_template'] = 'invalid_template'
    
    response = client.get('/download-pdf')
    assert response.status_code == 400
    assert b'Invalid template selected' in response.data

def test_download_pdf_missing_template(client, sample_resume_data):
    with client.session_transaction() as sess:
        sess['resume_data'] = sample_resume_data
        # Don't set selected_template
    
    response = client.get('/download-pdf')
    assert response.status_code == 400
    assert b'Please fill out the resume form first' in response.data

@pytest.mark.skipif(get_wkhtmltopdf_path() is None,
                    reason="wkhtmltopdf not installed")
def test_download_pdf_success(client, sample_resume_data):
    with client.session_transaction() as sess:
        sess['resume_data'] = sample_resume_data
        sess['selected_template'] = 'template1'
    
    response = client.get('/download-pdf')
    assert response.status_code in [200, 503]  # 503 if wkhtmltopdf not found
    if response.status_code == 200:
        assert response.mimetype == 'application/pdf'