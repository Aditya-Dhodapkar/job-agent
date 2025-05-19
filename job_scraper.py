import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import platform
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class JobScraper:
    def __init__(self):
        self.driver = None

    def setup_driver(self):
        """Initialize the Chrome WebDriver with appropriate options."""
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        # Create Chrome driver directly
        self.driver = webdriver.Chrome(options=chrome_options)

    def scrape_job_description(self, url):
        """
        Scrape job description from various job posting sites.
        Currently supports LinkedIn, Indeed, and generic job sites.
        """
        try:
            self.driver.get(url)
            time.sleep(3)  # Allow page to load

            # Extract job details based on the website
            if "linkedin.com/jobs" in url:
                return self._scrape_linkedin_job()
            elif "indeed.com" in url:
                return self._scrape_indeed_job()
            else:
                return self._scrape_generic_job()

        except Exception as e:
            print(f"Error scraping job description: {str(e)}")
            return None

    def _scrape_linkedin_job(self):
        """Scrape job details from LinkedIn job posting."""
        try:
            # Wait for job description to load
            job_description = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "job-description"))
            )
            
            # Get job title
            title = self.driver.find_element(By.CLASS_NAME, "job-details-jobs-unified-top-card__job-title").text
            
            # Get company name
            company = self.driver.find_element(By.CLASS_NAME, "job-details-jobs-unified-top-card__company-name").text
            
            return {
                'title': title,
                'company': company,
                'description': job_description.text
            }
        except Exception as e:
            print(f"Error scraping LinkedIn job: {str(e)}")
            return None

    def _scrape_indeed_job(self):
        """Scrape job details from Indeed job posting."""
        try:
            # Wait for job description to load
            job_description = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "jobsearch-jobDescriptionText"))
            )
            
            # Get job title
            title = self.driver.find_element(By.CLASS_NAME, "jobsearch-JobInfoHeader-title").text
            
            # Get company name
            company = self.driver.find_element(By.CLASS_NAME, "jobsearch-CompanyInfoContainer").text
            
            return {
                'title': title,
                'company': company,
                'description': job_description.text
            }
        except Exception as e:
            print(f"Error scraping Indeed job: {str(e)}")
            return None

    def _scrape_generic_job(self):
        """Scrape job details from generic job posting sites."""
        try:
            # Try to find common job description elements
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Look for common job description containers
            description = None
            for container in ['job-description', 'jobDescription', 'description', 'content']:
                element = soup.find(class_=container)
                if element:
                    description = element.text
                    break
            
            if not description:
                description = soup.find('body').text
            
            return {
                'title': self.driver.title,
                'company': 'Unknown',  # Generic scraper might not find company name
                'description': description
            }
        except Exception as e:
            print(f"Error scraping generic job: {str(e)}")
            return None

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

            # Get all experience items
            experience_items = self.driver.find_elements(By.CSS_SELECTOR, "li.pvs-list__paged-list-item")
            print(f"Found {len(experience_items)} experience items.")

            experiences = []
            for item in experience_items:
                try:
                    title = item.find_element(By.CSS_SELECTOR, "span[aria-hidden='true']").text
                except NoSuchElementException:
                    title = ""
                try:
                    company = item.find_elements(By.CSS_SELECTOR, "span[aria-hidden='true']")[1].text
                except Exception:
                    company = ""
                try:
                    description = item.find_element(By.CSS_SELECTOR, ".pvs-entity__caption-wrapper, .pvs-entity__description").text
                except NoSuchElementException:
                    description = ""
                experiences.append({
                    'title': title,
                    'company': company,
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
    scraper = JobScraper()
    scraper.setup_driver()
    job_details = scraper.scrape_job_description("https://www.linkedin.com/jobs/view/example-job")
    print(job_details)
    scraper.close()