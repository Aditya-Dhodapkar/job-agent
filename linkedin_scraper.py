from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import os
from dotenv import load_dotenv
import platform

class LinkedInScraper:
    def __init__(self):
        load_dotenv()
        self.email = os.getenv('LINKEDIN_EMAIL')
        self.password = os.getenv('LINKEDIN_PASSWORD')
        self.driver = None

    def setup_driver(self):
        """Initialize the Chrome WebDriver with appropriate options."""
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        # Create Chrome driver directly
        self.driver = webdriver.Chrome(options=chrome_options)

    def login(self):
        """Login to LinkedIn with manual intervention option."""
        try:
            self.driver.get("https://www.linkedin.com/login")
            
            print("\nPlease login manually in the browser window.")
            print("You have 60 seconds to complete the login process...")
            
            # Wait for manual login to complete
            try:
                # Wait for the global nav element which indicates successful login
                WebDriverWait(self.driver, 60).until(
                    EC.presence_of_element_located((By.ID, "global-nav"))
                )
                print("Login successful!")
                return True
            except TimeoutException:
                print("Login timeout. Please try again.")
                return False
                
        except Exception as e:
            print(f"Login failed: {str(e)}")
            return False

    def get_full_experience(self, profile_url):
        """Scrape the full experience section from a LinkedIn profile."""
        try:
            self.driver.get(profile_url)
            time.sleep(3)  # Allow page to load

            # Click the "Show all experiences" button robustly
            try:
                show_more_button = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "navigation-index-see-all-experiences"))
                )
                show_more_button.click()
                print("Clicked 'Show all experiences' by ID.")
                time.sleep(2)
            except TimeoutException:
                try:
                    show_more_button = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Show all')]/ancestor::a"))
                    )
                    show_more_button.click()
                    print("Clicked 'Show all experiences' by span text.")
                    time.sleep(2)
                except TimeoutException:
                    print("No 'Show all' button found or already showing all experiences")

            # Try multiple selectors for experience items
            selectors = [
                "li.pvs-list__paged-list-item",
                "section#experience-section ul > li",
                "div.pvs-list__outer-container ul > li"
            ]
            experience_items = []
            for selector in selectors:
                try:
                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    experience_items = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if experience_items:
                        print(f"Found {len(experience_items)} experience items with selector: {selector}")
                        break
                except TimeoutException:
                    continue

            if not experience_items:
                print("No experience items found with any selector.")
                # Print a snippet of the HTML for debugging
                print(self.driver.page_source[:2000])

            experiences = []
            for item in experience_items:
                # Title
                try:
                    title = item.find_element(By.CSS_SELECTOR, "span[aria-hidden='true']").text
                except NoSuchElementException:
                    title = ""
                # Company
                try:
                    company = item.find_elements(By.CSS_SELECTOR, "span[aria-hidden='true']")[1].text
                except Exception:
                    company = ""
                # Duration (dates)
                try:
                    date_elem = item.find_element(By.CSS_SELECTOR, "span.t-14.t-normal.t-black--light")
                    duration_text = date_elem.text
                    # Example: "Feb 2024 - Present · 1 yr 4 mos"
                    date_range = duration_text.split("·")[0].strip()
                    duration = duration_text.split("·")[1].strip() if "·" in duration_text else ""
                    if "-" in date_range:
                        start, end = [d.strip() for d in date_range.split("-")]
                    else:
                        start, end = date_range, ""
                except Exception:
                    start, end, duration = "", "", ""
                # Description
                try:
                    description = item.find_element(By.CSS_SELECTOR, ".pvs-entity__description, .pvs-list__item--with-top-padding").text
                except NoSuchElementException:
                    description = ""
                experiences.append({
                    'title': title,
                    'company': company,
                    'start': start,
                    'end': end,
                    'duration': duration,
                    'description': description
                })

            return experiences

        except Exception as e:
            print(f"Error scraping experiences: {str(e)}")
            return []

    def close(self):
        """Close the browser."""
        if self.driver:
            self.driver.quit()

if __name__ == "__main__":
    # Example usage
    scraper = LinkedInScraper()
    scraper.setup_driver()
    if scraper.login():
        experiences = scraper.get_full_experience("https://www.linkedin.com/in/example-profile")
        print(experiences)
    scraper.close()