import spacy
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from difflib import get_close_matches

# Curated list of common tech/skills (expand as needed)
CURATED_SKILLS = [
    'python', 'java', 'golang', 'node.js', 'c++', 'c#', 'sql', 'kdb+', 'graphql', 'django', 'flask', 'spring',
    'machine learning', 'ml', 'deep learning', 'data science', 'distributed systems', 'backend', 'frontend',
    'aws', 'gcp', 'azure', 'docker', 'kubernetes', 'microservices', 'rest', 'api', 'cloud', 'linux', 'git',
    'leadership', 'team lead', 'project management', 'agile', 'scrum', 'ci/cd', 'testing', 'unit testing',
    'nlp', 'computer vision', 'sqlalchemy', 'rust', 'react', 'typescript', 'javascript', 'pytorch', 'tensorflow',
    'ads', 'ad delivery', 'ranking', 'retrieval', 'bid optimization', 'budget pacing', 'system design', 'pipelines',
    'data engineering', 'data platform', 'microservice', 'microservices', 'cloud', 'api', 'microservice', 'etl',
    'teamwork', 'collaboration', 'communication', 'ownership', 'problem solving', 'innovation', 'scalability',
    'fault-tolerant', 'robust', 'production systems', 'sql', 'database', 'databases', 'optimization', 'performance'
]

class JobMatcher:
    def __init__(self):
        # Download required NLTK data
        nltk.download('punkt')
        nltk.download('stopwords')
        nltk.download('wordnet')
        
        # Load spaCy model
        self.nlp = spacy.load('en_core_web_sm')
        
        # Initialize TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=5000
        )
        
        # Get stopwords
        self.stop_words = set(stopwords.words('english'))

    def preprocess_text(self, text):
        """Clean and preprocess text for analysis."""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text

    def extract_skills_from_text(self, text):
        """Extract skills from text using curated list and fuzzy matching."""
        found_skills = set()
        text = self.preprocess_text(text)
        for skill in CURATED_SKILLS:
            # Use fuzzy matching for leniency
            matches = get_close_matches(skill, text.split(), n=1, cutoff=0.85)
            if skill in text or matches:
                found_skills.add(skill)
        return found_skills

    def extract_all_skills(self, experiences):
        """Extract all skills from a list of experiences."""
        all_text = []
        for exp in experiences:
            all_text.append(exp.get('title', ''))
            all_text.append(exp.get('company', ''))
            all_text.append(exp.get('description', ''))
        combined = ' '.join(all_text)
        return self.extract_skills_from_text(combined)

    def extract_job_skills(self, job_description):
        """Extract skills from the job description using the curated list."""
        return self.extract_skills_from_text(job_description)

    def calculate_match_score(self, candidate_skills, job_skills):
        if not job_skills:
            return 0.0
        return len(candidate_skills & job_skills) / len(job_skills)

    def analyze_match(self, experiences, job_description):
        # Extract skills
        candidate_skills = self.extract_all_skills(experiences)
        job_skills = self.extract_job_skills(job_description)

        # Calculate match score
        match_score = self.calculate_match_score(candidate_skills, job_skills)

        # Justification logic
        justifications = []
        matching_skills = []
        missing_skills = []
        for skill in job_skills:
            if skill in candidate_skills:
                # Find which experience(s) mention this skill
                found_in = []
                for exp in experiences:
                    exp_text = f"{exp.get('title', '')} {exp.get('company', '')} {exp.get('description', '')}".lower()
                    if skill in exp_text:
                        found_in.append(exp.get('title', ''))
                justifications.append(f"{skill.title()}: Found in {', '.join(found_in) if found_in else 'profile'}.")
                matching_skills.append(skill)
            else:
                justifications.append(f"{skill.title()}: Not found in any experience.")
                missing_skills.append(skill)

        # Add a summary justification
        justifications.insert(0, f"Matched {len(matching_skills)} out of {len(job_skills)} required skills.")

        return {
            'match_score': round(match_score, 2),
            'justification': justifications,
            'matching_skills': matching_skills,
            'missing_skills': missing_skills,
            'total_required_skills': len(job_skills),
            'matching_skills_count': len(matching_skills)
        }

if __name__ == "__main__":
    # Example usage
    matcher = JobMatcher()
    
    # Example experiences
    experiences = [
        {
            'title': 'Senior Software Engineer',
            'company': 'Tech Corp',
            'description': 'Developed web applications using Python and Django. Led a team of 5 developers.'
        }
    ]
    
    # Example job description
    job_description = """
    We are looking for a Senior Software Engineer with experience in Python and web development.
    The ideal candidate should have team leadership experience and knowledge of Django framework.
    """
    
    analysis = matcher.analyze_match(experiences, job_description)
    print(analysis)