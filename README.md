# Court Data Fetcher & Mini-Dashboard

A web application that fetches and displays case metadata and orders/judgments from Indian courts.

## Chosen Court
**Delhi High Court** (https://delhihighcourt.nic.in/)

This application targets the Delhi High Court's case status portal to fetch case information, parties, dates, and order/judgment PDFs.

## Features

- **Simple Web Interface**: Form with dropdowns for Case Type, Case Number, and Filing Year
- **Case Data Fetching**: Programmatically requests court website and parses case information
- **Data Storage**: Logs queries and responses in SQLite database
- **PDF Downloads**: Allows downloading of linked order/judgment PDFs
- **Error Handling**: User-friendly messages for invalid cases or site issues
- **Responsive Design**: Modern, clean UI with Bootstrap styling

## Technical Stack

- **Backend**: Python Flask
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Database**: SQLite
- **Web Scraping**: Selenium WebDriver with Chrome
- **PDF Handling**: PyPDF2 for PDF processing
- **Environment**: Docker support included

## CAPTCHA Strategy

The Delhi High Court website uses a simple CAPTCHA system. Our approach:
1. **Automated CAPTCHA Solving**: Using 2captcha API service
2. **Manual Override**: Fallback option for manual CAPTCHA solving
3. **Session Management**: Maintains cookies and session state
4. **Rate Limiting**: Implements delays to avoid overwhelming the server

## Setup Instructions

### Prerequisites
- Python 3.8+
- Chrome browser
- ChromeDriver (automatically managed by webdriver-manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd court-data-fetcher
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   FLASK_APP=app.py
   FLASK_ENV=development
   SECRET_KEY=your-secret-key-here
   CAPTCHA_API_KEY=your-2captcha-api-key
   ```

5. **Initialize database**
   ```bash
   python init_db.py
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Access the application**
   Open your browser and go to `http://localhost:5000`

### Docker Setup

1. **Build the Docker image**
   ```bash
   docker build -t court-data-fetcher .
   ```

2. **Run the container**
   ```bash
   docker run -p 5000:5000 court-data-fetcher
   ```

## Sample Environment Variables

```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-super-secret-key-change-this
CAPTCHA_API_KEY=your-2captcha-api-key-here
DATABASE_URL=sqlite:///court_data.db
LOG_LEVEL=INFO
```

## Project Structure

```
court-data-fetcher/
├── app.py                 # Main Flask application
├── init_db.py            # Database initialization
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── .env.example          # Environment variables template
├── README.md             # This file
├── static/               # Static files (CSS, JS, images)
│   ├── css/
│   ├── js/
│   └── downloads/        # Downloaded PDFs
├── templates/            # HTML templates
├── utils/                # Utility modules
│   ├── court_scraper.py  # Web scraping logic
│   ├── captcha_solver.py # CAPTCHA handling
│   └── pdf_handler.py    # PDF processing
├── models/               # Database models
│   └── database.py       # Database schema
└── tests/                # Unit tests
    └── test_scraper.py
```

## Usage

1. **Access the application** at `http://localhost:5000`
2. **Select case details**:
   - Case Type (e.g., "Writ Petition", "Civil Appeal")
   - Case Number (e.g., "1234")
   - Filing Year (e.g., "2023")
3. **Submit the form** to fetch case information
4. **View results** including:
   - Party names
   - Filing and next hearing dates
   - Order/judgment PDF links
5. **Download PDFs** by clicking on the download links

## Error Handling

The application handles various error scenarios:
- **Invalid case numbers**: Clear error messages
- **Site downtime**: Graceful degradation with retry logic
- **CAPTCHA failures**: Manual override option
- **Network issues**: Connection timeout handling
- **Database errors**: Transaction rollback and logging

## Security Considerations

- No hard-coded secrets in the codebase
- Environment variables for sensitive data
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- Rate limiting to prevent abuse

## License

MIT License - see LICENSE file for details

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## Demo Video

A 5-minute demo video showing the end-to-end flow is available in the project documentation.

## Optional Extras Implemented

-  Dockerfile for containerization
-  Unit tests for core functionality
-  CI workflow (GitHub Actions)
-  Pagination for multiple orders
-  Error handling and logging
-  Responsive UI design 