from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class QueryLog(db.Model):
    """Model for logging search queries"""
    __tablename__ = 'query_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    case_type = db.Column(db.String(100), nullable=False)
    case_number = db.Column(db.String(50), nullable=False)
    filing_year = db.Column(db.String(4), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))  # IPv6 compatible
    user_agent = db.Column(db.Text)
    
    # Relationship to case data
    case_data = db.relationship('CaseData', backref='query_log', uselist=False)
    
    def __repr__(self):
        return f'<QueryLog {self.case_type}/{self.case_number}/{self.filing_year}>'

class CaseData(db.Model):
    """Model for storing case data and results"""
    __tablename__ = 'case_data'
    
    id = db.Column(db.Integer, primary_key=True)
    query_id = db.Column(db.Integer, db.ForeignKey('query_logs.id'), nullable=False)
    case_type = db.Column(db.String(100), nullable=False)
    case_number = db.Column(db.String(50), nullable=False)
    filing_year = db.Column(db.String(4), nullable=False)
    
    # Case information
    parties = db.Column(db.Text)  # JSON string of parties
    filing_date = db.Column(db.Date)
    next_hearing_date = db.Column(db.Date)
    orders = db.Column(db.Text)  # JSON string of orders/judgments
    
    # Metadata
    status = db.Column(db.String(20), default='pending')  # success, not_found, error
    raw_response = db.Column(db.Text)  # Raw response from court website
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<CaseData {self.case_type}/{self.case_number}/{self.filing_year}>'
    
    def to_dict(self):
        """Convert case data to dictionary"""
        import json
        return {
            'id': self.id,
            'case_type': self.case_type,
            'case_number': self.case_number,
            'filing_year': self.filing_year,
            'parties': json.loads(self.parties) if self.parties else [],
            'filing_date': self.filing_date.isoformat() if self.filing_date else None,
            'next_hearing_date': self.next_hearing_date.isoformat() if self.next_hearing_date else None,
            'orders': json.loads(self.orders) if self.orders else [],
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 