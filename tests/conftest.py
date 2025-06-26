import pytest
from app import app as flask_app
from werkzeug.datastructures import MultiDict
from io import BytesIO

@pytest.fixture
def app():
    flask_app.config.update({
        'TESTING': True,
        'SECRET_KEY': 'test_secret_key',
        'WTF_CSRF_ENABLED': False,
        'UPLOAD_FOLDER': 'tests/uploads',
        'MAX_CONTENT_LENGTH': 16 * 1024 * 1024  # 16MB max file size
    })
    return flask_app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def auth_client(client):
    """A client with a session context for testing authenticated routes"""
    with client.session_transaction() as sess:
        sess['logged_in'] = True
    return client

@pytest.fixture
def sample_image_file():
    """Create a sample image file for testing"""
    image_data = BytesIO(b'fake image data')
    return (image_data, 'test.jpg')

@pytest.fixture
def sample_form_data():
    """Create a sample form data for testing"""
    return MultiDict([
        ('name', 'Test User'),
        ('email', 'test@example.com'),
        ('phone', '+1234567890'),
        ('address', '123 Test St'),
        ('linkedin', 'https://linkedin.com/in/testuser'),
        ('github', 'https://github.com/testuser'),
        ('website', 'https://testuser.com'),
        ('summary', 'Test user summary'),
        ('skills', 'Python'),
        ('skills', 'Testing'),
        ('course_name', 'Test Course'),
        ('institution_name', 'Test University'),
        ('edu_from', '2020-01'),
        ('edu_to', '2024-01')
    ])

@pytest.fixture
def mock_session(monkeypatch):
    """Mock Flask session for testing"""
    mock_data = {}
    
    def mock_get(key, default=None):
        return mock_data.get(key, default)
    
    def mock_set(key, value):
        mock_data[key] = value
    
    monkeypatch.setattr('flask.session.get', mock_get)
    monkeypatch.setattr('flask.session.__setitem__', mock_set)
    return mock_data

@pytest.fixture
def cleanup_uploads(app):
    """Clean up uploaded files after tests"""
    import shutil
    import os
    
    # Create uploads directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    yield
    
    # Clean up after test
    shutil.rmtree(app.config['UPLOAD_FOLDER'])
    os.makedirs(app.config['UPLOAD_FOLDER'])