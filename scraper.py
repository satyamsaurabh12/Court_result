from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
import re
from logger import logger

import time

def scrape_case(case_type, case_number, case_year):
    logger.info(f"Scraping started for {case_type} {case_number}/{case_year}")
    chrome_options = Options()
    # Run headless in environments without display
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(20)

        driver.get("https://delhihighcourt.nic.in/app/get-case-type-status")
        logger.info("Opened Delhi High Court case status page")
        time.sleep(2)

        driver.find_element(By.NAME, "case_type").send_keys(case_type)
        driver.find_element(By.NAME, "case_number").send_keys(case_number)
        driver.find_element(By.NAME, "case_year").send_keys(case_year)
        logger.info("Entered case details in form")

        try:
            captcha_text = driver.find_element(By.ID, "captcha-code").text.strip()
            driver.find_element(By.NAME, "captchaInput").send_keys(captcha_text)
            logger.info("Entered captcha text from page")
        except NoSuchElementException:
            logger.warning("Captcha not present or could not be read; proceeding without it")

        driver.find_element(By.ID, "search").click()
        logger.info("Clicked on search button")
        time.sleep(3)

        try:
            table = driver.find_element(By.CLASS_NAME, "table")
        except NoSuchElementException:
            logger.warning("Results table not found — possibly invalid query or site changed")
            return {
                "case_type": case_type,
                "case_number": case_number,
                "case_year": case_year,
                "parties": "Not available",
                "filing_date": "Not available",
                "hearing_date": None,
                "pdf_link": None,
            }

        rows = table.find_elements(By.TAG_NAME, "tr")
        if len(rows) < 2:
            logger.warning("No data rows in results table")
            return {
                "case_type": case_type,
                "case_number": case_number,
                "case_year": case_year,
                "parties": "Not available",
                "filing_date": "Not available",
                "hearing_date": None,
                "pdf_link": None,
            }

        cols = rows[1].find_elements(By.TAG_NAME, "td")
        parties = cols[2].text if len(cols) > 2 else "Not available"
        next_col_text = cols[3].text if len(cols) > 3 else ""
        match = re.search(r"NEXT DATE:\s*([^\s]+)", next_col_text)
        hearing_date = match.group(1) if match else None
        logger.info(f"Extracted parties: {parties}")
        logger.info(f"Extracted hearing date: {hearing_date}")

        try:
            a_tags = cols[1].find_elements(By.TAG_NAME, "a") if len(cols) > 1 else []
            if a_tags:
                last_link = a_tags[-1]
                driver.execute_script("arguments[0].click();", last_link)
                logger.info("Clicked on last available order link")
        except WebDriverException:
            logger.warning("Could not click order link")

        time.sleep(2)

        pdf_link = None
        try:
            table2 = driver.find_element(By.ID, "caseTable")
            rows2 = table2.find_elements(By.CSS_SELECTOR, "tbody tr")
            if rows2:
                cols2 = rows2[0].find_elements(By.TAG_NAME, "td")
                a_tags2 = cols2[1].find_elements(By.TAG_NAME, "a") if len(cols2) > 1 else []
                if a_tags2:
                    pdf_link = a_tags2[-1].get_attribute("href")
                    logger.info(f"Found PDF link: {pdf_link}")
        except NoSuchElementException:
            logger.warning("No PDF link found in case details table")

        return {
            "case_type": case_type,
            "case_number": case_number,
            "case_year": case_year,
            "parties": parties,
            "filing_date": "Not available",
            "hearing_date": hearing_date,
            "pdf_link": pdf_link,
        }
    except (TimeoutException, WebDriverException) as driver_error:
        logger.error(f"Web driver error: {driver_error}")
        return {
            "case_type": case_type,
            "case_number": case_number,
            "case_year": case_year,
            "parties": "Not available",
            "filing_date": "Not available",
            "hearing_date": None,
            "pdf_link": None,
        }
    finally:
        try:
            if driver:
                driver.quit()
        except Exception:
            pass
