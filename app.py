import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import json
import traceback

# Import our custom modules
from utils.court_scraper import DelhiHighCourtScraper
from utils.pdf_handler import PDFHandler
from models.database import db, QueryLog, CaseData

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///court_data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize database
db.init_app(app)

# Initialize scraper and PDF handler
scraper = DelhiHighCourtScraper()
pdf_handler = PDFHandler()

@app.route('/')
def index():
    """Main page with case search form"""
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_case():
    """Handle case search form submission"""
    try:
        # Get form data
        case_type = request.form.get('case_type')
        case_number = request.form.get('case_number')
        filing_year = request.form.get('filing_year')
        
        # Validate inputs
        if not all([case_type, case_number, filing_year]):
            flash('All fields are required', 'error')
            return redirect(url_for('index'))
        
        # Log the query
        query_log = QueryLog(
            case_type=case_type,
            case_number=case_number,
            filing_year=filing_year,
            timestamp=datetime.utcnow(),
            ip_address=request.remote_addr
        )
        db.session.add(query_log)
        db.session.commit()
        
        # Search for case data
        logger.info(f"Searching for case: {case_type}/{case_number}/{filing_year}")
        
        # Use the scraper to fetch case data
        case_data = scraper.search_case(case_type, case_number, filing_year)
        
        if case_data:
            # Save case data to database
            case_record = CaseData(
                query_id=query_log.id,
                case_type=case_type,
                case_number=case_number,
                filing_year=filing_year,
                parties=json.dumps(case_data.get('parties', [])),
                filing_date=case_data.get('filing_date'),
                next_hearing_date=case_data.get('next_hearing_date'),
                orders=json.dumps(case_data.get('orders', [])),
                raw_response=json.dumps(case_data),
                status='success'
            )
            db.session.add(case_record)
            db.session.commit()
            
            return render_template('results.html', case_data=case_data, query_id=query_log.id)
        else:
            # Log failed search
            case_record = CaseData(
                query_id=query_log.id,
                case_type=case_type,
                case_number=case_number,
                filing_year=filing_year,
                status='not_found',
                raw_response='Case not found'
            )
            db.session.add(case_record)
            db.session.commit()
            
            flash('Case not found. Please check the case details and try again.', 'error')
            return redirect(url_for('index'))
            
    except Exception as e:
        logger.error(f"Error during case search: {str(e)}")
        logger.error(traceback.format_exc())
        flash('An error occurred while searching for the case. Please try again.', 'error')
        return redirect(url_for('index'))

@app.route('/download/<path:pdf_url>')
def download_pdf(pdf_url):
    """Download PDF file"""
    try:
        # Decode the URL
        import urllib.parse
        pdf_url = urllib.parse.unquote(pdf_url)
        
        # Download and serve the PDF
        pdf_path = pdf_handler.download_pdf(pdf_url)
        
        if pdf_path and os.path.exists(pdf_path):
            return send_file(
                pdf_path,
                as_attachment=True,
                download_name=os.path.basename(pdf_url)
            )
        else:
            flash('PDF file not found or could not be downloaded.', 'error')
            return redirect(url_for('index'))
            
    except Exception as e:
        logger.error(f"Error downloading PDF: {str(e)}")
        flash('Error downloading PDF file.', 'error')
        return redirect(url_for('index'))

@app.route('/api/case-types')
def get_case_types():
    """API endpoint to get available case types"""
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
    return jsonify(case_types)

@app.route('/api/years')
def get_years():
    """API endpoint to get available years"""
    current_year = datetime.now().year
    years = list(range(current_year, current_year - 20, -1))
    return jsonify(years)

@app.route('/history')
def search_history():
    """Show search history"""
    try:
        # Get recent searches (last 50)
        recent_searches = QueryLog.query.order_by(QueryLog.timestamp.desc()).limit(50).all()
        return render_template('history.html', searches=recent_searches)
    except Exception as e:
        logger.error(f"Error fetching search history: {str(e)}")
        flash('Error loading search history.', 'error')
        return redirect(url_for('index'))

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'database': 'connected' if db.engine.pool.checkedin() else 'disconnected'
    })

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    logger.error(f"Internal server error: {str(error)}")
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Run the application
    app.run(debug=os.getenv('FLASK_ENV') == 'development', host='0.0.0.0', port=5000) 