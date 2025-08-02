"""
Pytest configuration for Court Data Fetcher tests
"""

import sys
import os
import pytest
from unittest.mock import Mock, patch

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture(scope="session")
def app():
    """Create a test Flask app"""
    from app import app as flask_app
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with flask_app.app_context():
        from models.database import db
        db.create_all()
        yield flask_app
        db.drop_all()

@pytest.fixture
def client(app):
    """Create a test client"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create a test CLI runner"""
    return app.test_cli_runner()

@pytest.fixture(autouse=True)
def mock_selenium():
    """Mock Selenium WebDriver to avoid actual browser interactions"""
    with patch('utils.court_scraper.webdriver.Chrome') as mock_chrome:
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        yield mock_chrome

@pytest.fixture(autouse=True)
def mock_requests():
    """Mock requests to avoid actual HTTP calls"""
    with patch('utils.captcha_solver.requests.get') as mock_get:
        mock_response = Mock()
        mock_response.content = b"fake image data"
        mock_get.return_value = mock_response
        yield mock_get 