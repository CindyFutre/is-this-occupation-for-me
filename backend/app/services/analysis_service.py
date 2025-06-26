import nltk
import re
from typing import List, Dict, Any, Set, Tuple
from collections import defaultdict, Counter
from app.models.pydantic_models import JobInsightsReport, AnalyzedTerm
import html

# Download required NLTK data on first import
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

class TermAnalyzer:
    """
    Core analysis engine for processing job postings and extracting insights.
    """
    
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        
        # Custom normalization dictionary for synonyms and variations
        self.normalization_dict = {
            # Programming languages and frameworks
            'javascript': 'javascript',
            'js': 'javascript',
            'node.js': 'node.js',
            'nodejs': 'node.js',
            'react.js': 'react',
            'reactjs': 'react',
            'vue.js': 'vue',
            'vuejs': 'vue',
            'angular.js': 'angular',
            'angularjs': 'angular',
            
            # Microsoft Office
            'ms excel': 'excel',
            'microsoft excel': 'excel',
            'ms word': 'word',
            'microsoft word': 'word',
            'ms powerpoint': 'powerpoint',
            'microsoft powerpoint': 'powerpoint',
            'ms office': 'microsoft office',
            'microsoft office': 'microsoft office',
            
            # Databases
            'mysql': 'mysql',
            'postgresql': 'postgresql',
            'postgres': 'postgresql',
            'mongodb': 'mongodb',
            'mongo': 'mongodb',
            
            # Cloud platforms
            'amazon web services': 'aws',
            'aws': 'aws',
            'google cloud platform': 'gcp',
            'google cloud': 'gcp',
            'gcp': 'gcp',
            'microsoft azure': 'azure',
            'azure': 'azure',
            
            # Common skills
            'machine learning': 'machine learning',
            'ml': 'machine learning',
            'artificial intelligence': 'artificial intelligence',
            'ai': 'artificial intelligence',
            'data analysis': 'data analysis',
            'data analytics': 'data analysis',
            'project management': 'project management',
            'project manager': 'project management',
            
            # Education levels
            'bachelor\'s degree': 'bachelor\'s degree',
            'bachelors degree': 'bachelor\'s degree',
            'bachelor degree': 'bachelor\'s degree',
            'master\'s degree': 'master\'s degree',
            'masters degree': 'master\'s degree',
            'master degree': 'master\'s degree',
            'phd': 'phd',
            'ph.d': 'phd',
            'doctorate': 'phd',
            
            # Experience levels
            'years of experience': 'years experience',
            'years experience': 'years experience',
            'work experience': 'experience',
            'professional experience': 'experience',
        }
        
        # Category keywords for classification
        self.category_keywords = {
            'responsibilities': {
                'develop', 'design', 'implement', 'create', 'build', 'maintain', 'manage', 
                'lead', 'coordinate', 'oversee', 'execute', 'deliver', 'analyze', 'research',
                'collaborate', 'communicate', 'present', 'report', 'document', 'test',
                'troubleshoot', 'support', 'monitor', 'optimize', 'improve', 'ensure',
                'responsible', 'duties', 'tasks', 'activities', 'functions', 'role'
            },
            'skills': {
                'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node.js',
                'sql', 'mysql', 'postgresql', 'mongodb', 'aws', 'azure', 'gcp',
                'docker', 'kubernetes', 'git', 'linux', 'windows', 'excel', 'powerpoint',
                'tableau', 'power bi', 'machine learning', 'data analysis', 'statistics',
                'communication', 'leadership', 'teamwork', 'problem solving', 'analytical',
                'technical', 'programming', 'coding', 'software', 'tools', 'technologies'
            },
            'qualifications': {
                'degree', 'bachelor', 'master', 'phd', 'education', 'certification',
                'certified', 'license', 'years experience', 'experience', 'background',
                'knowledge', 'understanding', 'familiarity', 'proficiency', 'expertise',
                'required', 'preferred', 'minimum', 'qualifications', 'requirements',
                'must have', 'should have', 'nice to have'
            },
            'unique_aspects': {
                'remote', 'hybrid', 'flexible', 'startup', 'enterprise', 'fortune',
                'benefits', 'salary', 'compensation', 'equity', 'stock options',
                'culture', 'environment', 'opportunity', 'growth', 'career',
                'innovative', 'cutting edge', 'state of the art', 'industry leading',
                'competitive', 'bonus', 'vacation', 'pto', 'health insurance'
            }
        }
    
    def normalize_term(self, term: str) -> str:
        """
        Normalize a term using custom rules and dictionary.
        """
        # Convert to lowercase
        term = term.lower().strip()
        
        # Remove special characters but keep spaces, hyphens, and periods
        term = re.sub(r'[^\w\s\-\.]', '', term)
        
        # Check normalization dictionary
        if term in self.normalization_dict:
            return self.normalization_dict[term]
        
        return term
    
    def clean_html_and_artifacts(self, text: str) -> str:
        """
        Clean HTML tags, script content, and other artifacts from text.
        """
        if not text:
            return ""
        
        # Decode HTML entities
        text = html.unescape(text)
        
        # Remove script tags and their content
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove style tags and their content
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove HTML tags but keep the content
        text = re.sub(r'<[^>]+>', ' ', text)
        
        # Remove common tracking/analytics patterns
        tracking_patterns = [
            r'https?://[^\s]*\.cloudfront\.net[^\s]*',
            r'https?://[^\s]*analytics[^\s]*',
            r'https?://[^\s]*tracking[^\s]*',
            r'data-[a-zA-Z-]+=[\"\'][^\"\']*[\"\']',
            r'id=["\'][^"\']*detrack[^"\']*["\']',
            r'defer\s+src=',
            r'script\s+id=',
        ]
        
        for pattern in tracking_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Remove URLs
        text = re.sub(r'https?://\S+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+\.\S+', '', text)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def extract_terms_from_text(self, text: str) -> List[Tuple[str, str]]:
        """
        Extract and normalize terms from text.
        Returns list of (normalized_term, original_sentence) tuples.
        """
        if not text:
            return []
        
        # Clean HTML and artifacts first
        text = self.clean_html_and_artifacts(text)
        
        terms_with_context = []
        sentences = sent_tokenize(text)
        
        for sentence in sentences:
            # Skip sentences that are too short or contain artifacts
            if len(sentence.strip()) < 10:
                continue
            
            # Skip sentences with HTML/script artifacts
            if any(artifact in sentence.lower() for artifact in ['script', 'detrack', 'defer', 'src=', 'data-g=']):
                continue
            
            # Tokenize the sentence
            tokens = word_tokenize(sentence.lower())
            
            # Extract meaningful terms (2-4 word phrases and single words)
            for i in range(len(tokens)):
                # Single words
                if len(tokens[i]) > 2 and tokens[i] not in self.stop_words:
                    # Skip technical artifacts
                    if any(artifact in tokens[i] for artifact in ['script', 'detrack', 'defer', 'src', 'http']):
                        continue
                    
                    normalized = self.normalize_term(tokens[i])
                    if normalized and len(normalized) > 2:
                        terms_with_context.append((normalized, sentence))
                
                # 2-word phrases
                if i < len(tokens) - 1:
                    phrase = f"{tokens[i]} {tokens[i+1]}"
                    
                    # Skip phrases with artifacts
                    if any(artifact in phrase for artifact in ['script', 'detrack', 'defer', 'src', 'http']):
                        continue
                    
                    if not any(word in self.stop_words for word in [tokens[i], tokens[i+1]]):
                        normalized = self.normalize_term(phrase)
                        if normalized and len(normalized) > 3:
                            terms_with_context.append((normalized, sentence))
                
                # 3-word phrases
                if i < len(tokens) - 2:
                    phrase = f"{tokens[i]} {tokens[i+1]} {tokens[i+2]}"
                    
                    # Skip phrases with artifacts
                    if any(artifact in phrase for artifact in ['script', 'detrack', 'defer', 'src', 'http']):
                        continue
                    
                    if not any(word in self.stop_words for word in [tokens[i], tokens[i+1], tokens[i+2]]):
                        normalized = self.normalize_term(phrase)
                        if normalized and len(normalized) > 4:
                            terms_with_context.append((normalized, sentence))
        
        return terms_with_context
    
    def categorize_term(self, term: str, context_sentences: List[str]) -> str:
        """
        Categorize a term based on keywords and context.
        """
        term_lower = term.lower()
        
        # Check direct keyword matches
        for category, keywords in self.category_keywords.items():
            if any(keyword in term_lower for keyword in keywords):
                return category
        
        # Context-based categorization
        context_text = ' '.join(context_sentences).lower()
        
        category_scores = defaultdict(int)
        
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword in context_text:
                    category_scores[category] += 1
        
        # Return category with highest score, default to 'unique_aspects'
        if category_scores:
            return max(category_scores.items(), key=lambda x: x[1])[0]
        
        return 'unique_aspects'
    
    def generate_report_from_postings(self, postings: List[Dict[str, Any]], searched_title: str, soc_code: str) -> JobInsightsReport:
        """
        Generate a complete JobInsightsReport from raw job postings.
        """
        if not postings:
            return JobInsightsReport(
                searched_title=searched_title,
                soc_code=soc_code,
                total_postings_analyzed=0,
                responsibilities=[],
                skills=[],
                qualifications=[],
                unique_aspects=[]
            )
        
        # Track terms and their contexts
        term_contexts = defaultdict(lambda: {'count': 0, 'sentences': set(), 'postings': set()})
        
        # Process each job posting
        for i, posting in enumerate(postings):
            # Extract text from various fields
            text_fields = []
            
            # Get job description (main content)
            if posting.get('Description'):
                text_fields.append(posting['Description'])
            elif posting.get('description'):
                text_fields.append(posting['description'])
            
            # Get job title and company for additional context
            if posting.get('JobTitle'):
                text_fields.append(posting['JobTitle'])
            elif posting.get('job_title'):
                text_fields.append(posting['job_title'])
            
            # Combine all text and clean it
            combined_text = ' '.join(text_fields)
            combined_text = self.clean_html_and_artifacts(combined_text)
            
            # Extract terms from this posting
            terms_with_context = self.extract_terms_from_text(combined_text)
            
            # Track unique terms per posting (count once per posting)
            posting_terms = set()
            
            for term, sentence in terms_with_context:
                if term not in posting_terms:
                    posting_terms.add(term)
                    term_contexts[term]['count'] += 1
                    term_contexts[term]['postings'].add(i)
                
                # Always add sentences for context (up to 3 per term)
                if len(term_contexts[term]['sentences']) < 3:
                    term_contexts[term]['sentences'].add(sentence)
        
        # Categorize and rank terms
        categorized_terms = {
            'responsibilities': [],
            'skills': [],
            'qualifications': [],
            'unique_aspects': []
        }
        
        for term, data in term_contexts.items():
            # Filter out technical artifacts and meaningless terms
            if any(artifact in term.lower() for artifact in [
                'script', 'detrack', 'defer', 'src', 'http', 'www', '.com', '.net',
                'data-g', 'id=', 'class=', 'div', 'span', 'href', 'onclick'
            ]):
                continue
            
            # Only include terms that appear in at least 2 postings or have count >= 3
            if data['count'] >= 2:
                category = self.categorize_term(term, list(data['sentences']))
                
                # Clean context sentences
                clean_sentences = []
                for sentence in list(data['sentences'])[:3]:
                    clean_sentence = self.clean_html_and_artifacts(sentence)
                    if len(clean_sentence) > 20:  # Only include substantial sentences
                        clean_sentences.append(clean_sentence)
                
                if clean_sentences:  # Only add if we have clean context
                    analyzed_term = AnalyzedTerm(
                        term=term,
                        count=data['count'],
                        context_sentences=clean_sentences
                    )
                    
                    categorized_terms[category].append(analyzed_term)
        
        # Sort each category by count (descending) and limit to top 15
        for category in categorized_terms:
            categorized_terms[category].sort(key=lambda x: x.count, reverse=True)
            categorized_terms[category] = categorized_terms[category][:15]
        
        return JobInsightsReport(
            searched_title=searched_title,
            soc_code=soc_code,
            total_postings_analyzed=len(postings),
            responsibilities=categorized_terms['responsibilities'],
            skills=categorized_terms['skills'],
            qualifications=categorized_terms['qualifications'],
            unique_aspects=categorized_terms['unique_aspects']
        )


# Global analyzer instance
analyzer = TermAnalyzer()

def generate_report_from_postings(postings: List[Dict[str, Any]], searched_title: str, soc_code: str) -> JobInsightsReport:
    """
    Public interface for generating reports from job postings.
    """
    return analyzer.generate_report_from_postings(postings, searched_title, soc_code)