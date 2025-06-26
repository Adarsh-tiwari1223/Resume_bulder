import pytest
from app import app
from flask import session

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
        'summary': 'Experienced software developer'
    }

def test_preview_resume_without_data(client):
    response = client.get('/preview-resume')
    assert response.status_code == 302  # Redirect to form
    assert b'/form' in response.headers['Location'].encode()

def test_preview_resume_without_template(client, sample_resume_data):
    with client.session_transaction() as sess:
        sess['resume_data'] = sample_resume_data
        # Don't set selected_template
    
    response = client.get('/preview-resume')
    assert response.status_code == 302  # Redirect to form

def test_preview_resume_success(client, sample_resume_data):
    with client.session_transaction() as sess:
        sess['resume_data'] = sample_resume_data
        sess['selected_template'] = 'template1'

    response = client.get('/preview-resume')
    assert response.status_code == 200
    assert b'John Doe' in response.data
    # Contact details removed from header, so email may not be present
    # assert b'john@example.com' in response.data

def test_template_selection(client):
    response = client.get('/select-template')
    assert response.status_code == 200
    
    # Test template selection submission
    response = client.post('/select-template', data={'template': 'template1'})
    assert response.status_code == 302  # Redirect to preview
    assert b'/preview-resume' in response.headers['Location'].encode()

@pytest.mark.parametrize('template_name', [
    'template1',
    'template2',
    'template3',
    'template19'
])
def test_specific_template_rendering(client, sample_resume_data, template_name):
    with client.session_transaction() as sess:
        sess['resume_data'] = sample_resume_data
        sess['selected_template'] = template_name
    
    response = client.get('/preview-resume')
    assert response.status_code == 200
    # Check for common elements that should be in all templates
    assert b'John Doe' in response.data
    assert b'Python' in response.data  # From skills_list