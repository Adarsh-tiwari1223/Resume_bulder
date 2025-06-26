import pytest
from app import process_form_data
from werkzeug.datastructures import MultiDict, FileStorage
from io import BytesIO

@pytest.fixture
def sample_form_data():
    return MultiDict([
        ('name', 'John Doe'),
        ('email', 'john@example.com'),
        ('phone', '+1234567890'),
        ('address', '123 Test St'),
        ('linkedin', 'https://linkedin.com/in/johndoe'),
        ('course_name', 'Computer Science'),
        ('institution_name', 'Test University'),
        ('edu_from', '2020-01'),
        ('edu_to', '2024-01'),
        ('skills', 'Python'),
        ('skills', 'Flask'),
        ('skills', 'Testing')
    ])

@pytest.fixture
def sample_files():
    photo_content = BytesIO(b'fake image content')
    photo = FileStorage(
        stream=photo_content,
        filename='profile.jpg',
        content_type='image/jpeg'
    )
    return {'profile_photo': photo}

def test_process_form_data_valid(sample_form_data, sample_files):
    result = process_form_data(sample_form_data, sample_files)
    assert result['name'] == 'John Doe'
    assert result['email'] == 'john@example.com'
    assert result['phone'] == '+1234567890'
    assert len(result['skills_list']) == 3
    assert 'Python' in result['skills_list']
    assert result['education'][0]['course_name'] == 'Computer Science'

def test_process_form_data_missing_required(sample_form_data):
    # Remove required field
    sample_form_data.pop('name')
    with pytest.raises(ValueError, match='Please fill all required fields'):
        process_form_data(sample_form_data, {})

def test_process_form_data_invalid_email(sample_form_data):
    sample_form_data['email'] = 'invalid-email'
    with pytest.raises(ValueError, match='Please enter a valid email address'):
        process_form_data(sample_form_data, {})

def test_process_form_data_invalid_phone(sample_form_data):
    sample_form_data['phone'] = '123'
    with pytest.raises(ValueError, match='Please enter a valid phone number'):
        process_form_data(sample_form_data, {})

def test_process_form_data_invalid_photo(sample_form_data):
    invalid_photo = FileStorage(
        stream=BytesIO(b'fake image content'),
        filename='profile.txt',
        content_type='text/plain'
    )
    with pytest.raises(ValueError, match='Invalid file type for photo'):
        process_form_data(sample_form_data, {'profile_photo': invalid_photo})