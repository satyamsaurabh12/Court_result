from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import re
from logger import logger

import time

def scrape_case(case_type, case_number, case_year):
    logger.info(f"Scraping started for {case_type} {case_number}/{case_year}")
    chrome_options = Options()
    driver = webdriver.Chrome(options=chrome_options)

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
        logger.info(f"Entered captcha: {captcha_text}")
    except:
        print("Captcha not found")
        logger.warning("Captcha not found or could not be read")

    driver.find_element(By.ID, "search").click()
    logger.info("Clicked on search button")
    time.sleep(3)

    table = driver.find_element(By.CLASS_NAME, "table")
    rows = table.find_elements(By.TAG_NAME, "tr")

    cols = rows[1].find_elements(By.TAG_NAME, "td")
    parties = cols[2].text
    hearing_date = cols[3].text
    match = re.search(r"NEXT DATE:\s*([^\s]+)", cols[3].text)
    hearing_date = match.group(1) if match else None
    logger.info(f"Extracted parties: {parties}")
    logger.info(f"Extracted hearing date: {hearing_date}")

    try:
        a_tags = cols[1].find_elements(By.TAG_NAME, "a")
        if a_tags:
            last_link = a_tags[-1]
            driver.execute_script("arguments[0].click();", last_link)
            logger.info("Clicked on last available order link")
    except:
        logger.warning("No order link found to click")
        

    time.sleep(3)

    pdf_link = None
    try:
        table2 = driver.find_element(By.ID, "caseTable")
        rows2 = table2.find_elements(By.CSS_SELECTOR, "tbody tr")
        if rows2:
            cols = rows2[0].find_elements(By.TAG_NAME, "td")
            a_tags = cols[1].find_elements(By.TAG_NAME, "a")
            if a_tags:
                pdf_link = a_tags[-1].get_attribute("href")
                logger.info(f"Found PDF link: {pdf_link}")
    except:
        logger.warning("No PDF link found in case details table")
        

    driver.quit()
    logger.info(f"Scraping completed for {case_type} {case_number}/{case_year}")



    return {
        "case_type": case_type,
        "case_number": case_number,
        "case_year": case_year,
        "parties": parties,
        "filing_date": "NULL",
        "hearing_date": hearing_date,
        "pdf_link": pdf_link,
    }
