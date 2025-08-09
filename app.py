from flask import Flask, render_template, request
from models import db, CourtQuery
from scraper import scrape_case
from logger import logger

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///court_data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

with app.app_context():
    db.create_all()
    logger.info("Database tables created or verified.")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Keep the existing business logic for case_type
        case_type = "CS(OS)"
        case_number = (request.form.get("case_number") or "").strip()
        case_year = (request.form.get("case_year") or "").strip()
        logger.info(f"Received case query: {case_type} {case_number}/{case_year}")

        # Basic input validation
        if not case_number or not case_year:
            logger.warning("Validation failed: Missing case number or year")
            return render_template("form.html", error_message="Please provide both Case Number and Filing Year.")
        if not case_number.isdigit():
            logger.warning("Validation failed: Case number must be numeric")
            return render_template("form.html", error_message="Case Number must be numeric.")
        if not (case_year.isdigit() and len(case_year) == 4):
            logger.warning("Validation failed: Invalid filing year")
            return render_template("form.html", error_message="Filing Year must be a 4-digit year (e.g., 2023).")

        try:
            # Try DB first
            query = CourtQuery.query.filter_by(
                case_type=case_type,
                case_number=case_number,
                case_year=case_year
            ).first()

            if query:
                logger.info("Found case in database, returning stored result.")
                result_payload = {
                    "case_type": query.case_type,
                    "case_number": query.case_number,
                    "case_year": query.case_year,
                    "parties": query.parties,
                    "filing_date": query.filing_date,
                    "hearing_date": query.hearing_date,
                    "pdf_link": query.pdf_link,
                }
                return render_template("result.html", **result_payload)

            # Fall back to scraping if not in DB
            logger.warning("Case not found in database. Scraping from web...")
            result = scrape_case(case_type, case_number, case_year)

            # Persist result defensively
            try:
                new_entry = CourtQuery(**result)
                db.session.add(new_entry)
                db.session.commit()
            except Exception as db_err:
                db.session.rollback()
                logger.error(f"Database error while saving scraped result: {db_err}")

            return render_template("result.html", **result)
        except Exception as e:
            logger.error(f"Unhandled error while processing request: {e}")
            return render_template("form.html", error_message="We couldn't fetch this case right now. Please try again later.")
        
    logger.info("Rendering search form page.")
    return render_template("form.html")

@app.errorhandler(404)
def not_found(_error):
    logger.warning("404 Not Found")
    return render_template("error.html", code=404, message="The requested page was not found."), 404

@app.errorhandler(500)
def internal_error(_error):
    logger.error("500 Internal Server Error")
    return render_template("error.html", code=500, message="An unexpected error occurred. Please try again later."), 500

if __name__ == "__main__":
    logger.info("Starting Flask server...")
    app.run(debug=True)
