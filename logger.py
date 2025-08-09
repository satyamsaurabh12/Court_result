import logging
import os

# Create logs directory if not exists
if not os.path.exists("logs"):
    os.makedirs("logs")

# Logger configuration
logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG for more details
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("CourtScraperApp")
