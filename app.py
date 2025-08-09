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
        case_type = "W.P.(C)"
        case_number = request.form["case_number"]
        case_year = request.form["case_year"]
        logger.info(f"Received case query: {case_type} {case_number}/{case_year}")

        query = CourtQuery.query.filter_by(
            case_type=case_type,
            case_number=case_number,
            case_year=case_year
        ).first()

        if query:
            logger.info("Found case in database, returning stored result.")
            print("✅ Found in DB")
            # print(**query.__dict__)
            return render_template("result.html", **query.__dict__)
        else:
            print("🕵️ Scraping from web...")
            logger.warning("Case not found in database. Scraping from web...")
            result = scrape_case(case_type, case_number, case_year)
            new_entry = CourtQuery(**result)
            db.session.add(new_entry)
            db.session.commit()
            return render_template("result.html", **result)
        
    logger.info("Rendering search form page.")
    return render_template("form.html")

if __name__ == "__main__":
    logger.info("Starting Flask server...")
    app.run(debug=True)
