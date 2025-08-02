import unittest
import sys
import os
from unittest.mock import Mock, patch

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

class TestApp(unittest.TestCase):
    """Test cases for Flask app"""
    
    def setUp(self):
        """Set up test fixtures"""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
    
    def test_index_page(self):
        """Test that the index page loads"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Court Data Fetcher', response.data)
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('timestamp', data)
    
    def test_case_types_api(self):
        """Test case types API endpoint"""
        response = self.client.get('/api/case-types')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertIn("Writ Petition (Civil)", data)
    
    def test_years_api(self):
        """Test years API endpoint"""
        response = self.client.get('/api/years')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
    
    def test_history_page(self):
        """Test history page loads"""
        response = self.client.get('/history')
        self.assertEqual(response.status_code, 200)
    
    @patch('app.scraper.search_case')
    def test_search_case_success(self, mock_search):
        """Test successful case search"""
        # Mock successful case search
        mock_search.return_value = {
            'parties': ['Petitioner', 'Respondent'],
            'filing_date': '2023-01-01',
            'next_hearing_date': '2023-02-01',
            'orders': ['Order 1', 'Order 2']
        }
        
        response = self.client.post('/search', data={
            'case_type': 'Writ Petition (Civil)',
            'case_number': '123',
            'filing_year': '2023'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
    
    @patch('app.scraper.search_case')
    def test_search_case_failure(self, mock_search):
        """Test failed case search"""
        # Mock failed case search
        mock_search.return_value = None
        
        response = self.client.post('/search', data={
            'case_type': 'Writ Petition (Civil)',
            'case_number': '999',
            'filing_year': '2023'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
    
    def test_search_case_missing_fields(self):
        """Test case search with missing fields"""
        response = self.client.post('/search', data={
            'case_type': 'Writ Petition (Civil)',
            'case_number': '',
            'filing_year': '2023'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main() 