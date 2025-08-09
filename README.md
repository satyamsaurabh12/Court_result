# 🏛 Delhi High Court Case Scraper

A **Flask-based web application** that allows you to search Delhi High Court case details by **Case Number** and **Year**.  
It uses **Selenium** to scrape data from the official court website, stores it in an **SQLite** database, and displays the results in a simple web interface.  

If a case is already in the database, it loads from there instead of scraping again — saving time and reducing unnecessary website requests.

---

## 📂 Project Structure
```
court-case-scraper/
│
├── app.py              # Main Flask application
├── models.py           # Database model
├── scraper.py          # Selenium scraping logic
├── logger.py           # Logging configuration
├── requirements.txt    # Python dependencies
│
├── templates/
│   ├── form.html       # Search form page
│   └── result.html     # Results display page
│
├── logs/
│   └── app.log         # Generated log file
│
└── README.md
```

---

## ⚙️ Setup Instructions

### 1️⃣ Create a Virtual Environment
```bash
python -m venv venv
```

Activate the environment:

**Windows (PowerShell)**
```powershell
venv\Scripts\activate
```

**Mac/Linux**
```bash
source venv/bin/activate
```

---

### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

---

### 3️⃣ Install ChromeDriver
1. Install **Google Chrome**.
2. Download the **ChromeDriver** version matching your Chrome browser from:  
   [https://chromedriver.chromium.org/downloads](https://chromedriver.chromium.org/downloads)
3. Add ChromeDriver to your system **PATH** or place it in the project root directory.

---

## 🛠 CAPTCHA Strategy
The Delhi High Court currently uses a plain-text CAPTCHA (not an image), which makes it straightforward to handle in code.

1. Find the CAPTCHA element  
2. Extract its value using:

```python
captcha_value = driver.find_element(By.ID, "captchaText").text.strip()
```
3. Enter the value into the CAPTCHA input field:

```python
driver.find_element(By.ID, "captchaInput").send_keys(captcha_value)
```   

---

## 🚀 Running the Application
```bash
python app.py
```

Once running, open your browser and visit:
```
http://127.0.0.1:5000/
```

---

## 🔍 How It Works
1. User enters **Case Number** and **Year** in the form.
2. The app checks the **SQLite** database for an existing entry.
3. If found → Loads data directly from the database.
4. If not found → Scrapes case details from the Delhi High Court website using Selenium.
5. Saves scraped data to the database.
6. Displays case details in the browser.
7. All events are logged in `logs/app.log`.

---

## 📌 Features
- **Flask** web framework
- **Selenium** for automated web scraping
- **SQLite** database for persistent storage
- **Centralized logging** to both console and log file
- **Simple HTML templates** for search and results display