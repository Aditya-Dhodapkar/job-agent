import os
from linkedin_scraper import LinkedInScraper
from job_scraper import JobScraper
from job_matcher import JobMatcher
from llm_matcher import llm_match_score
import argparse
import json
from datetime import datetime

def save_results(results, output_file=None):
    """Save results to a JSON file in the 'output' directory."""
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"job_match_results_{timestamp}.json"
    output_path = os.path.join(output_dir, output_file)
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Job Experience Matcher')
    parser.add_argument('--linkedin-profile', required=True, help='LinkedIn profile URL')
    parser.add_argument('--job-url', required=True, help='Job posting URL')
    parser.add_argument('--output', help='Output file path for results')
    args = parser.parse_args()

    print("Initializing components...")
    linkedin_scraper = LinkedInScraper()
    job_scraper = JobScraper()
    matcher = JobMatcher()

    try:
        print("\nSetting up LinkedIn scraper...")
        linkedin_scraper.setup_driver()
        
        print("Logging into LinkedIn...")
        if not linkedin_scraper.login():
            print("Failed to login to LinkedIn. Please check your credentials.")
            return

        print("\nScraping LinkedIn profile experiences...")
        experiences = linkedin_scraper.get_full_experience(args.linkedin_profile)
        if not experiences:
            print("No experiences found or failed to scrape experiences.")
            return

        print("\nSetting up job scraper...")
        job_scraper.setup_driver()
        
        print("Scraping job description...")
        job_details = job_scraper.scrape_job_description(args.job_url)
        if not job_details:
            print("Failed to scrape job description.")
            return

        print("\nAnalyzing match between experiences and job requirements...")
        analysis = matcher.analyze_match(experiences, job_details['description'])

        # LLM-based analysis
        print("\nRequesting LLM-powered match analysis (this may take a few seconds)...")
        llm_result = llm_match_score(experiences, job_details['description'])
        print("\n=== LLM Match Analysis ===")
        print(llm_result)

        # Prepare results
        results = {
            'job_details': job_details,
            'experiences': experiences,
            'analysis': analysis,
            'llm_analysis': llm_result
        }

        # Print summary
        print("\n=== Match Analysis Summary ===")
        print(f"Overall Match Score: {analysis['match_score']*100:.2f}%")
        print(f"Skills Match: {analysis['matching_skills_count']} out of {analysis['total_required_skills']} required skills")
        
        print("\nMatching Skills:")
        for skill in analysis['matching_skills']:
            print(f"- {skill}")
        
        print("\nMissing Skills:")
        for skill in analysis['missing_skills']:
            print(f"- {skill}")

        print("\nJustification:")
        for line in analysis['justification']:
            print("-", line)

        # Save results
        save_results(results, args.output)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        # Clean up
        linkedin_scraper.close()
        job_scraper.close()

if __name__ == "__main__":
    main() 