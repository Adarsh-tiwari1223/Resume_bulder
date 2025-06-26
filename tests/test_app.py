import os
import pytest
from app import app, validate_email, validate_phone, allowed_file, clean_filename

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    rv = client.get('/')
    assert rv.status_code == 200

def test_validate_email():
    assert validate_email('test@example.com') == True
    assert validate_email('invalid-email') == False
    assert validate_email('test@domain') == False
    assert validate_email('@domain.com') == False

def test_validate_phone():
    assert validate_phone('+1234567890') == True
    assert validate_phone('12345') == False
    assert validate_phone('abcdefghijk') == False

def test_allowed_file():
    assert allowed_file('test.pdf') == True
    assert allowed_file('test.doc') == True
    assert allowed_file('test.docx') == True
    assert allowed_file('test.jpg') == True
    assert allowed_file('test.txt') == False

def test_clean_filename():
    filename = 'test file.pdf'
    cleaned = clean_filename(filename)
    assert '.pdf' in cleaned
    assert ' ' not in cleaned
    assert cleaned.startswith('20')

def test_form_submission(client):
    data = {
        'name': 'Test User',
        'email': 'test@example.com',
        'phone': '+1234567890',
        'address': '123 Test St',
        'linkedin': 'https://linkedin.com/in/testuser',
        'skills': ['Python', 'Flask', 'Testing'],
        'course_name': 'Computer Science',
        'institution_name': 'Test University',
        'edu_from': '2020-01',
        'edu_to': '2024-01'
    }
    rv = client.post('/form', data=data)
    assert rv.status_code in [200, 302]  # Success or redirect