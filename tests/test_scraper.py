import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.court_scraper import DelhiHighCourtScraper
from utils.captcha_solver import CaptchaSolver
from utils.pdf_handler import PDFHandler

class TestDelhiHighCourtScraper(unittest.TestCase):
    """Test cases for Delhi High Court Scraper"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.scraper = DelhiHighCourtScraper()
    
    def test_init(self):
        """Test scraper initialization"""
        self.assertIsNotNone(self.scraper)
        self.assertEqual(self.scraper.base_url, "https://delhihighcourt.nic.in/")
        self.assertEqual(self.scraper.case_status_url, "https://delhihighcourt.nic.in/case-status")
    
    @patch('utils.court_scraper.webdriver.Chrome')
    @patch('utils.court_scraper.ChromeDriverManager')
    def test_setup_driver_success(self, mock_chrome_manager, mock_chrome):
        """Test successful WebDriver setup"""
        mock_chrome_manager.return_value.install.return_value = "/path/to/chromedriver"
        mock_chrome.return_value = Mock()
        
        result = self.scraper._setup_driver()
        
        self.assertTrue(result)
        self.assertIsNotNone(self.scraper.driver)
    
    @patch('utils.court_scraper.webdriver.Chrome')
    def test_setup_driver_failure(self, mock_chrome):
        """Test WebDriver setup failure"""
        mock_chrome.side_effect = Exception("Chrome not found")
        
        result = self.scraper._setup_driver()
        
        self.assertFalse(result)
        self.assertIsNone(self.scraper.driver)
    
    def test_get_case_types(self):
        """Test getting available case types"""
        case_types = self.scraper.get_case_types()
        
        self.assertIsInstance(case_types, list)
        self.assertGreater(len(case_types), 0)
        self.assertIn("Writ Petition (Civil)", case_types)
        self.assertIn("Civil Appeal", case_types)
    
    @patch('utils.court_scraper.BeautifulSoup')
    def test_extract_case_data_success(self, mock_bs4):
        """Test successful case data extraction"""
        # Mock BeautifulSoup response
        mock_soup = Mock()
        mock_soup.find.return_value = None
        mock_bs4.return_value = mock_soup
        
        page_source = "<html><body>Test page</body></html>"
        result = self.scraper._extract_case_data(page_source)
        
        self.assertIsInstance(result, dict)
        self.assertIn('parties', result)
        self.assertIn('filing_date', result)
        self.assertIn('next_hearing_date', result)
        self.assertIn('orders', result)
    
    def test_extract_case_data_failure(self):
        """Test case data extraction failure"""
        result = self.scraper._extract_case_data("invalid html")
        
        self.assertIsNone(result)

class TestCaptchaSolver(unittest.TestCase):
    """Test cases for CAPTCHA Solver"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.solver = CaptchaSolver()
    
    def test_init(self):
        """Test CAPTCHA solver initialization"""
        self.assertIsNotNone(self.solver)
        self.assertEqual(self.solver.api_url, "http://2captcha.com/in.php")
        self.assertEqual(self.solver.result_url, "http://2captcha.com/res.php")
    
    @patch('utils.captcha_solver.requests.get')
    def test_download_captcha_success(self, mock_get):
        """Test successful CAPTCHA download"""
        mock_response = Mock()
        mock_response.content = b"fake image data"
        mock_get.return_value = mock_response
        
        result = self.solver._download_captcha("http://example.com/captcha.png")
        
        self.assertIsNotNone(result)
    
    @patch('utils.captcha_solver.requests.get')
    def test_download_captcha_failure(self, mock_get):
        """Test CAPTCHA download failure"""
        mock_get.side_effect = Exception("Network error")
        
        result = self.solver._download_captcha("http://example.com/captcha.png")
        
        self.assertIsNone(result)
    
    def test_validate_captcha_valid(self):
        """Test valid CAPTCHA validation"""
        valid_captchas = ["ABC123", "123456", "abc123"]
        
        for captcha in valid_captchas:
            result = self.solver.validate_captcha(captcha)
            self.assertTrue(result)
    
    def test_validate_captcha_invalid(self):
        """Test invalid CAPTCHA validation"""
        invalid_captchas = ["", "123", "ABCDEFGHIJK", "ABC@123", None]
        
        for captcha in invalid_captchas:
            result = self.solver.validate_captcha(captcha)
            self.assertFalse(result)

class TestPDFHandler(unittest.TestCase):
    """Test cases for PDF Handler"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.pdf_handler = PDFHandler()
    
    def test_init(self):
        """Test PDF handler initialization"""
        self.assertIsNotNone(self.pdf_handler)
        self.assertIn('downloads', self.pdf_handler.downloads_dir)
    
    def test_generate_filename(self):
        """Test filename generation"""
        url = "http://example.com/document.pdf"
        filename = self.pdf_handler._generate_filename(url)
        
        self.assertIsInstance(filename, str)
        self.assertTrue(filename.endswith('.pdf'))
        self.assertIn('document', filename)
    
    def test_generate_filename_no_extension(self):
        """Test filename generation for URL without extension"""
        url = "http://example.com/document"
        filename = self.pdf_handler._generate_filename(url)
        
        self.assertIsInstance(filename, str)
        self.assertTrue(filename.endswith('.pdf'))
    
    def test_generate_filename_fallback(self):
        """Test filename generation fallback"""
        url = "http://example.com/"
        filename = self.pdf_handler._generate_filename(url)
        
        self.assertIsInstance(filename, str)
        self.assertTrue(filename.startswith('court_document_'))
        self.assertTrue(filename.endswith('.pdf'))
    
    @patch('utils.pdf_handler.os.path.exists')
    def test_get_pdf_info_exists(self, mock_exists):
        """Test getting PDF info for existing file"""
        mock_exists.return_value = True
        
        with patch('utils.pdf_handler.os.path.getsize') as mock_size:
            mock_size.return_value = 1024
            
            with patch('utils.pdf_handler.os.path.getmtime') as mock_time:
                mock_time.return_value = 1234567890
                
                result = self.pdf_handler.get_pdf_info("/path/to/file.pdf")
                
                self.assertIsNotNone(result)
                self.assertEqual(result['size'], 1024)
    
    @patch('utils.pdf_handler.os.path.exists')
    def test_get_pdf_info_not_exists(self, mock_exists):
        """Test getting PDF info for non-existent file"""
        mock_exists.return_value = False
        
        result = self.pdf_handler.get_pdf_info("/path/to/nonexistent.pdf")
        
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main() 