#!/usr/bin/env python3
"""
Demo script for Court Data Fetcher
This script demonstrates the core functionality of the application
"""

import os
import sys
import json
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def demo_scraper():
    """Demo the scraper functionality"""
    print("Demo: Court Scraper")
    print("=" * 40)
    
    try:
        from utils.court_scraper import DelhiHighCourtScraper
        
        scraper = DelhiHighCourtScraper()
        case_types = scraper.get_case_types()
        
        print(f"Available case types: {len(case_types)}")
        for i, case_type in enumerate(case_types[:5], 1):
            print(f"  {i}. {case_type}")
        print("  ...")
        
        print("\nScraper demo completed!")
        return True
        
    except Exception as e:
        print(f"Scraper demo failed: {str(e)}")
        return False

def demo_captcha_solver():
    """Demo the CAPTCHA solver"""
    print("\nDemo: CAPTCHA Solver")
    print("=" * 40)
    
    try:
        from utils.captcha_solver import CaptchaSolver
        
        solver = CaptchaSolver()
        
        # Test CAPTCHA validation
        test_captchas = ["ABC123", "123456", "abc123", "", "ABC@123"]
        
        for captcha in test_captchas:
            is_valid = solver.validate_captcha(captcha)
            status = "Valid" if is_valid else "Invalid"
            print(f"  '{captcha}': {status}")
        
        print("\nCAPTCHA solver demo completed!")
        return True
        
    except Exception as e:
        print(f"CAPTCHA solver demo failed: {str(e)}")
        return False

def demo_pdf_handler():
    """Demo the PDF handler"""
    print("\nDemo: PDF Handler")
    print("=" * 40)
    
    try:
        from utils.pdf_handler import PDFHandler
        
        pdf_handler = PDFHandler()
        
        # Test filename generation
        test_urls = [
            "http://example.com/document.pdf",
            "http://example.com/document",
            "http://example.com/"
        ]
        
        for url in test_urls:
            filename = pdf_handler._generate_filename(url)
            print(f"  URL: {url}")
            print(f"  Generated filename: {filename}")
            print()
        
        print("PDF handler demo completed!")
        return True
        
    except Exception as e:
        print(f"PDF handler demo failed: {str(e)}")
        return False

def demo_database():
    """Demo the database functionality"""
    print("\nDemo: Database Models")
    print("=" * 40)
    
    try:
        from models.database import QueryLog, CaseData
        
        # Create sample data
        sample_query = QueryLog(
            case_type="Writ Petition (Civil)",
            case_number="1234",
            filing_year="2023",
            timestamp=datetime.utcnow(),
            ip_address="127.0.0.1"
        )
        
        sample_case = CaseData(
            query_id=1,
            case_type="Writ Petition (Civil)",
            case_number="1234",
            filing_year="2023",
            parties=json.dumps([
                {"type": "Petitioner", "name": "John Doe"},
                {"type": "Respondent", "name": "State of Delhi"}
            ]),
            filing_date="2023-01-15",
            next_hearing_date="2023-12-20",
            orders=json.dumps([
                {"date": "2023-01-15", "title": "Initial Order", "url": "http://example.com/order1.pdf"}
            ]),
            status="success"
        )
        
        print("Sample Query Log:")
        print(f"  Case: {sample_query.case_type}/{sample_query.case_number}/{sample_query.filing_year}")
        print(f"  Timestamp: {sample_query.timestamp}")
        
        print("\nSample Case Data:")
        print(f"  Status: {sample_case.status}")
        print(f"  Parties: {len(json.loads(sample_case.parties))} parties")
        print(f"  Orders: {len(json.loads(sample_case.orders))} orders")
        
        print("\nDatabase demo completed!")
        return True
        
    except Exception as e:
        print(f"Database demo failed: {str(e)}")
        return False

def demo_web_interface():
    """Demo the web interface components"""
    print("\nDemo: Web Interface")
    print("=" * 40)
    
    try:
        # Check if templates exist
        template_files = [
            "templates/base.html",
            "templates/index.html",
            "templates/results.html",
            "templates/history.html"
        ]
        
        for template in template_files:
            if os.path.exists(template):
                print(f"   {template}")
            else:
                print(f"   {template}")
        
        # Check if static files exist
        static_files = [
            "static/css/style.css",
            "static/js/main.js"
        ]
        
        print("\nStatic files:")
        for static_file in static_files:
            if os.path.exists(static_file):
                print(f"   {static_file}")
            else:
                print(f"   {static_file}")
        
        print("\nWeb interface demo completed!")
        return True
        
    except Exception as e:
        print(f"Web interface demo failed: {str(e)}")
        return False

def main():
    """Main demo function"""
    print("Court Data Fetcher - Demo")
    print("=" * 50)
    print("This demo showcases the core functionality of the application.\n")
    
    demos = [
        ("Scraper", demo_scraper),
        ("CAPTCHA Solver", demo_captcha_solver),
        ("PDF Handler", demo_pdf_handler),
        ("Database", demo_database),
        ("Web Interface", demo_web_interface)
    ]
    
    results = []
    
    for name, demo_func in demos:
        try:
            success = demo_func()
            results.append((name, success))
        except Exception as e:
            print(f" {name} demo crashed: {str(e)}")
            results.append((name, False))
    
    # Summary
    print("\n Demo Summary")
    print("=" * 50)
    
    passed = 0
    for name, success in results:
        status = " PASSED" if success else " FAILED"
        print(f"{name}: {status}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} demos passed")
    
    if passed == len(results):
        print("\nAll demos passed! The application is ready to use.")
        print("\nTo run the application:")
        print("  1. python init_db.py")
        print("  2. python app.py")
        print("  3. Open http://localhost:5000 in your browser")
    else:
        print("\nSome demos failed. Please check the errors above.")
    
    return passed == len(results)

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 