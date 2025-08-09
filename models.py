from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from logger import logger

db = SQLAlchemy()
logger.info("Creating  a database\n")
class CourtQuery(db.Model):
    __tablename__ = 'court_queries'

    id = db.Column(db.Integer, primary_key=True)
    case_type = db.Column(db.String(50))
    case_number = db.Column(db.String(50))
    case_year = db.Column(db.String(10))
    parties = db.Column(db.Text)
    filing_date = db.Column(db.String(50))
    hearing_date = db.Column(db.String(50))
    pdf_link = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
