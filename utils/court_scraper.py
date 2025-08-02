import time
import logging
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import re
from datetime import datetime
import os
from utils.captcha_solver import CaptchaSolver

logger = logging.getLogger(__name__)

class DelhiHighCourtScraper:
    """Scraper for Delhi High Court case status portal"""
    
    def __init__(self):
        self.base_url = "https://delhihighcourt.nic.in/"
        self.case_status_url = "https://delhihighcourt.nic.in/case-status"
        self.driver = None
        self.captcha_solver = CaptchaSolver()
        
    def _setup_driver(self):
        """Setup Chrome WebDriver with appropriate options"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in headless mode
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            
            # Setup ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.implicitly_wait(10)
            
            logger.info("Chrome WebDriver setup completed")
            return True
            
        except Exception as e:
            logger.error(f"Error setting up WebDriver: {str(e)}")
            return False
    
    def _cleanup_driver(self):
        """Clean up WebDriver resources"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriver cleanup completed")
            except Exception as e:
                logger.error(f"Error during WebDriver cleanup: {str(e)}")
    
    def _solve_captcha(self, captcha_element):
        """Solve CAPTCHA using automated service or manual input"""
        try:
            # Get CAPTCHA image
            captcha_img = captcha_element.find_element(By.TAG_NAME, "img")
            captcha_src = captcha_img.get_attribute("src")
            
            # Try automated CAPTCHA solving
            captcha_text = self.captcha_solver.solve_captcha(captcha_src)
            
            if captcha_text:
                # Fill CAPTCHA input
                captcha_input = captcha_element.find_element(By.NAME, "captcha")
                captcha_input.clear()
                captcha_input.send_keys(captcha_text)
                logger.info("CAPTCHA solved automatically")
                return True
            else:
                logger.warning("Automated CAPTCHA solving failed, using manual fallback")
                return False
                
        except Exception as e:
            logger.error(f"Error solving CAPTCHA: {str(e)}")
            return False
    
    def _extract_case_data(self, page_source):
        """Extract case data from the page source"""
        try:
            soup = BeautifulSoup(page_source, 'html.parser')
            
            case_data = {
                'parties': [],
                'filing_date': None,
                'next_hearing_date': None,
                'orders': []
            }
            
            # Extract parties information
            parties_section = soup.find('div', {'class': 'parties-info'})
            if parties_section:
                party_elements = parties_section.find_all('div', {'class': 'party'})
                for party in party_elements:
                    party_type = party.find('span', {'class': 'party-type'})
                    party_name = party.find('span', {'class': 'party-name'})
                    if party_type and party_name:
                        case_data['parties'].append({
                            'type': party_type.text.strip(),
                            'name': party_name.text.strip()
                        })
            
            # Extract dates
            dates_section = soup.find('div', {'class': 'case-dates'})
            if dates_section:
                filing_date_elem = dates_section.find('span', {'class': 'filing-date'})
                if filing_date_elem:
                    case_data['filing_date'] = filing_date_elem.text.strip()
                
                next_hearing_elem = dates_section.find('span', {'class': 'next-hearing'})
                if next_hearing_elem:
                    case_data['next_hearing_date'] = next_hearing_elem.text.strip()
            
            # Extract orders/judgments
            orders_section = soup.find('div', {'class': 'orders-section'})
            if orders_section:
                order_elements = orders_section.find_all('div', {'class': 'order-item'})
                for order in order_elements:
                    order_date = order.find('span', {'class': 'order-date'})
                    order_title = order.find('span', {'class': 'order-title'})
                    order_link = order.find('a', {'class': 'order-link'})
                    
                    if order_date and order_title:
                        order_data = {
                            'date': order_date.text.strip(),
                            'title': order_title.text.strip(),
                            'url': order_link.get('href') if order_link else None
                        }
                        case_data['orders'].append(order_data)
            
            return case_data
            
        except Exception as e:
            logger.error(f"Error extracting case data: {str(e)}")
            return None
    
    def search_case(self, case_type, case_number, filing_year):
        """Search for case information"""
        try:
            if not self._setup_driver():
                return None
            
            logger.info(f"Searching for case: {case_type}/{case_number}/{filing_year}")
            
            # Navigate to case status page
            self.driver.get(self.case_status_url)
            time.sleep(2)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "case-search-form"))
            )
            
            # Fill case type dropdown
            case_type_select = self.driver.find_element(By.NAME, "case_type")
            case_type_select.click()
            case_type_option = self.driver.find_element(By.XPATH, f"//option[contains(text(), '{case_type}')]")
            case_type_option.click()
            
            # Fill case number
            case_number_input = self.driver.find_element(By.NAME, "case_number")
            case_number_input.clear()
            case_number_input.send_keys(case_number)
            
            # Fill filing year
            filing_year_input = self.driver.find_element(By.NAME, "filing_year")
            filing_year_input.clear()
            filing_year_input.send_keys(filing_year)
            
            # Handle CAPTCHA
            captcha_element = self.driver.find_element(By.CLASS_NAME, "captcha-container")
            captcha_solved = self._solve_captcha(captcha_element)
            
            if not captcha_solved:
                # Manual CAPTCHA handling
                logger.info("Waiting for manual CAPTCHA input...")
                time.sleep(30)  # Give user time to solve CAPTCHA manually
            
            # Submit form
            submit_button = self.driver.find_element(By.TYPE, "submit")
            submit_button.click()
            
            # Wait for results
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CLASS_NAME, "case-results")),
                        EC.presence_of_element_located((By.CLASS_NAME, "no-results"))
                    )
                )
            except TimeoutException:
                logger.error("Timeout waiting for search results")
                return None
            
            # Check if case was found
            no_results = self.driver.find_elements(By.CLASS_NAME, "no-results")
            if no_results:
                logger.info("Case not found")
                return None
            
            # Extract case data
            case_data = self._extract_case_data(self.driver.page_source)
            
            if case_data:
                logger.info("Case data extracted successfully")
                return case_data
            else:
                logger.error("Failed to extract case data")
                return None
                
        except Exception as e:
            logger.error(f"Error during case search: {str(e)}")
            return None
        finally:
            self._cleanup_driver()
    
    def get_case_types(self):
        """Get available case types from the court website"""
        case_types = [
            "Writ Petition (Civil)",
            "Writ Petition (Criminal)",
            "Civil Appeal",
            "Criminal Appeal",
            "Civil Suit",
            "Criminal Case",
            "Company Petition",
            "Arbitration Petition",
            "Tax Case",
            "Service Matter"
        ]
        return case_types 